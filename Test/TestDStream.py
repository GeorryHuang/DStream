from DStream import  *
from Helper import *
import unittest
import sys
from HelperForTest import *
sys.path.append("..")


class TestDStream(unittest.TestCase):
    def test_init(self):
        dstream=D_Stream()
        self.assertEqual(0,dstream.tc)
        self.assertEqual(Helper().gap(), dstream.gap)
        self.assertNotEqual(None,dstream.grid_list)
        self.assertNotEqual(None, dstream.cluster_manager)
    def test_adjust_sparse(self):
        #被删除的grid不存在
        dstream=D_Stream()
        grid=Grid()
        grid._Grid__key=1
        with self.assertRaises(KeyError):
            dstream._D_Stream__adjust_sparse(grid)
        #被删除的grid存在且其cluster是single
            #构造cluster
        cluster=Cluster(1)
        key=Helper.getKey(60,3,30)
        g=Grid()
        g._Grid__key=key
        cluster.addGrid(g)
        keys = Helper.getNeighborKeys(key)
        for k in keys:
            grid=Grid()
            grid._Grid__key=k
            cluster.addGrid(grid)
        manager=dstream._D_Stream__cluster_manager
        manager._ClusterManager__cluster_key_index=1
        manager._ClusterManager__cluster_dic[1]=cluster
        dstream._D_Stream__adjust_sparse(g)
        self.assertEqual(1,len(manager._ClusterManager__cluster_dic))
        #被删除的grid存在且删除grid后不是single
        cluster = Cluster(1)
        key = '1999232137'
        g = Grid()
        g._Grid__key = key
        cluster.addGrid(g)
        grid=Grid()
        grid._Grid__key='2000232137'
        cluster.addGrid(grid)
        grid = Grid()
        grid._Grid__key = '1998232137'
        cluster.addGrid(grid)
        manager = dstream._D_Stream__cluster_manager
        manager._ClusterManager__cluster_key_index = 1
        manager._ClusterManager__cluster_dic[1] = cluster
        dstream._D_Stream__adjust_sparse(g)
        self.assertEqual(2, len(manager._ClusterManager__cluster_dic))
    def test_adjust_dense_neighbor_dense(self):
        dstream = D_Stream()
        manager=dstream.cluster_manager
        #建立一个dense grid和一个邻居gird_h，grid_h是dense且grid的cluster不存在，验证是否g会在h的cluster里
        g=Grid()
        g._Grid__key='1001001001'
        h=Grid()
        h._Grid__key='1002001001'
        h._Grid__densityStatus=DensityStatus.DENSE
        manager.addNewCluster(h)
        dstream._D_Stream__adjust_dense_neighbor_dense(g,h)
        cluster=manager.getCluster(1)
        self.assertEqual(len(cluster.getAllGrids()),2)
        h1=cluster.getGrid('456')
        self.assertEqual(h1.key(),'456')
        #建立一个dense grid和一个邻居gird_h，g的cluster比h的大，验证h的cluster被g吞并
        dstream = D_Stream()
        manager = dstream.cluster_manager
        g=Grid()
        h=Grid()
        g._Grid__key='1002001001'
        h._Grid__key='1003001001'
        g._Grid__densityStatus=DensityStatus.DENSE
        manager.addNewCluster(g)
        manager.addNewCluster(h)
        cluster_g=manager.getCluster(1)
        g1=Grid()
        g1._Grid__key='1004001001'
        g2=Grid()
        g2._Grid__key='1003002001'
        cluster_g.addGrid(g1)
        cluster_g.addGrid(g2)
        dstream._D_Stream__adjust_dense_neighbor_dense(g, h)
        self.assertEqual(1,len(manager.getAllCluster()))
        clu=manager.getAllCluster()
        gs=clu.getAllGrids()
        for grid in gs:
            self.assertIn(grid.key(),['1002001001','1003001001','1004001001','1003002001'])
        #建立一个dense grid和一个邻居gird_h，h的cluster比g大，验证g的cluster 被h吞并
        dstream = D_Stream()
        manager = dstream.cluster_manager
        g = Grid()
        h = Grid()
        g._Grid__key = '1002001001'
        h._Grid__key = '1003001001'
        g._Grid__densityStatus = DensityStatus.DENSE
        manager.addNewCluster(g)
        manager.addNewCluster(h)
        cluster_h = manager.getCluster(2)
        h1 = Grid()
        h1._Grid__key = '1004001001'
        h2 = Grid()
        h2._Grid__key = '1003002001'
        cluster_h.addGrid(h1)
        cluster_h.addGrid(h2)
        dstream._D_Stream__adjust_dense_neighbor_dense(g, h)
        self.assertEqual(1, len(manager.getAllCluster()))
        clu = manager.getAllCluster()
        gs = clu.getAllGrids()
        for grid in gs:
            self.assertIn(grid.key(), ['1002001001', '1003001001', '1004001001', '1003002001'])

    def test_adjust_dense_neighbor_transitional(self):
        #另dense g没有cluster，且如果g加入到邻居h的cluster里，那么邻居h是一个outside，验证g在h的cluster里
        dstream = D_Stream()
        manager = dstream.cluster_manager
        g=Grid()
        g._Grid__densityStatus=DensityStatus.DENSE
        g._Grid__key='1000100100'
        h=Grid()
        h._Grid__key='1001100100'
        manager.addNewCluster(h)
        h1=Grid()
        h1._Grid__key='1002100100'
        cluster=manager.getCluster(1)
        cluster.addGrid(h1)
        dstream._D_Stream__adjust_dense_neighbor_transitional(g,h)
        grids=cluster.getAllGrids()
        for grid in grids:
            self.assertIn(grid,['1000100100','1001100100','1002100100'])

        #另dense g没有cluster，且如果g加入到邻居h的cluster里，那么邻居h不是一个outside，验证g不在h的cluster里
        dstream = D_Stream()
        manager = dstream.cluster_manager
        g = Grid()
        g._Grid__densityStatus=DensityStatus.DENSE
        g._Grid__key = '1000100100'
        h = Grid()
        h._Grid__key = '1001100100'
        manager.addNewCluster(h)
        h1 = Grid()
        h1._Grid__key = '1002100100'
        h2 = Grid()
        h2._Grid__key = '1001101100'
        h3 = Grid()
        h3._Grid__key = '1001099100'
        h4 = Grid()
        h4._Grid__key = '1001100099'
        h5 = Grid()
        h5._Grid__key = '1001100101'
        cluster = manager.getCluster(1)
        cluster.addGrid(h1)
        cluster.addGrid(h2)
        cluster.addGrid(h3)
        cluster.addGrid(h4)
        cluster.addGrid(h5)
        dstream._D_Stream__adjust_dense_neighbor_transitional(g, h)
        grids = cluster.getAllGrids()
        self.assertEqual(len(grids),6)
        for grid in grids:
            self.assertIn(grid, ['1001100100', '1002100100', '1001101100','1001099100','1001100099','1001100101'])
        self.assertEqual(-1,g._Grid__cluster_key)

        #另dense g有cluster且g的cluster比邻居h的cluster大
        dstream = D_Stream()
        manager = dstream.cluster_manager
        g = Grid()
        g._Grid__densityStatus = DensityStatus.DENSE
        g._Grid__key = '1000100100'
        h = Grid()
        h._Grid__key = '1001100100'
        manager.addNewCluster(g)
        manager.addNewCluster(h)
        cluster1=manager.getCluster(1)
        g1=Grid()
        g1._Grid__key='1241241'
        cluster1.addGrid(g1)
        dstream._D_Stream__adjust_dense_neighbor_transitional(g, h)
        self.assertEqual(len(cluster1),3)
        grids=cluster1.getAllGrids()
        for g in grids:
            self.assertIn(g.key(),['1000100100','1001100100','1241241'])
        self.assertEqual(1,len(manager.getAllCluster()))


    def test_adjust_dense(self):
        #两个neighbor cluster，一大一小,其中h是dense
        dstream = D_Stream()
        grid_list=dstream.grid_list
        manager=dstream.cluster_manager
        g=Grid()
        g._Grid__key='1000100100'

        c11=Grid()
        c11._Grid__key='1001100100'
        c12=Grid()
        c12._Grid__key='1002100100'
        cluster1=Cluster(1)
        cluster1.addGrid(c11)
        cluster1.addGrid(c12)
        manager._ClusterManager__cluster_dic[1]=cluster1
        manager._ClusterManager__cluster_key_index+=1
        grid_list[c11.key()]=c11
        grid_list[c12.key()]=c12

        c21 = Grid()
        c21._Grid__key = '1000101100'
        c21._Grid__densityStatus=DensityStatus.DENSE
        c22 = Grid()
        c22._Grid__key = '1000009100'
        c23 = Grid()
        c23._Grid__key = '1000009101'
        cluster2 = Cluster(2)
        cluster2.addGrid(c21)
        cluster2.addGrid(c22)
        cluster2.addGrid(c23)
        manager._ClusterManager__cluster_dic[2] = cluster1
        manager._ClusterManager__cluster_key_index += 1
        grid_list[c21.key()] = c21
        grid_list[c22.key()] = c22
        grid_list[c23.key()] = c23
        self.assertEqual(0,dstream._D_Stream__adjust_dense())

        #两个neighbor cluster，一大一小,其中h是transitional
        dstream = D_Stream()
        grid_list = dstream.grid_list
        manager = dstream.cluster_manager
        g = Grid()
        g._Grid__key = '1000100100'

        c11 = Grid()
        c11._Grid__key = '1001100100'
        c12 = Grid()
        c12._Grid__key = '1002100100'
        cluster1 = Cluster(1)
        cluster1.addGrid(c11)
        cluster1.addGrid(c12)
        manager._ClusterManager__cluster_dic[1] = cluster1
        manager._ClusterManager__cluster_key_index += 1
        grid_list[c11.key()] = c11
        grid_list[c12.key()] = c12

        c21 = Grid()
        c21._Grid__key = '1000101100'
        c21._Grid__densityStatus = DensityStatus.TRANSITIONAL
        c22 = Grid()
        c22._Grid__key = '1000009100'
        c23 = Grid()
        c23._Grid__key = '1000009101'
        cluster2 = Cluster(2)
        cluster2.addGrid(c21)
        cluster2.addGrid(c22)
        cluster2.addGrid(c23)
        manager._ClusterManager__cluster_dic[2] = cluster1
        manager._ClusterManager__cluster_key_index += 1
        grid_list[c21.key()] = c21
        grid_list[c22.key()] = c22
        grid_list[c23.key()] = c23
        self.assertEqual(0,dstream._D_Stream__adjust_dense())

        #不存在neighbor cluster
        dstream = D_Stream()
        raw = HelperForTest.randomLegalRawData()
        key = Helper.getKeyFromRawData(raw)
        dstream.do_DStream(raw)
        grid = dstream.grid_list[key]
        dstream._D_Stream__adjust_dense(grid)
        self.assertEqual(-1,dstream._D_Stream__adjust_dense())

        #有neighbor但师neighbor没有cluster
        dstream = D_Stream()
        raw = HelperForTest.randomLegalRawData()
        key = Helper.getKeyFromRawData(raw)
        dstream.do_DStream(raw)
        grid = dstream.grid_list[key]
        keys=Helper.getNeighborKeys(key)
        for k in keys:
            g=Grid()
            g._Grid__key=k
            dstream.grid_list[k]=g
            break
        dstream._D_Stream__adjust_dense(grid)
        self.assertEqual(-2,dstream._D_Stream__adjust_dense())



    def test_adjust_transitional(self):
        #transitional g，g没有neighbor cluster但有neighbor 验证g没变化
        dstream = D_Stream()
        g=Grid()
        g._Grid__densityStatus=DensityStatus.TRANSITIONAL
        g._Grid__key='1000100100'
        h=Grid()
        h._Grid__key='1001100100'
        dstream._D_Stream__adjust_transitional(g)

        self.assertEqual(-1,g._Grid__cluster_key)




        #有neighbor cluster，但如果加入不是outside 验证g没被加入
        dstream = D_Stream()
        g = Grid()
        g._Grid__densityStatus = DensityStatus.TRANSITIONAL
        g._Grid__key = '1000100100'
        keys=Helper.getNeighborKeys(g.key())
        cluster1=Cluster(1)
        dstream.cluster_manager._ClusterManager__cluster_dic[1]=cluster1
        dstream.cluster_manager._ClusterManager__cluster_key_index+=1
        for k in keys:
            h=Grid()
            h._Grid__key=k
            cluster1.addGrid(h)
            dstream.grid_list[k]=h


        dstream._D_Stream__adjust_transitional(g)
        self.assertEqual(-1, g._Grid__cluster_key)

        #有neighbor cluster，加入是outside，验证g被加入
        dstream = D_Stream()
        g = Grid()
        g._Grid__densityStatus = DensityStatus.TRANSITIONAL
        g._Grid__key = '1000100100'
        keys = Helper.getNeighborKeys(g.key())
        cluster1 = Cluster(1)
        dstream.manager._ClusterManager__cluster_dic[1] = cluster1
        dstream.manager._ClusterManager__cluster_key_index+=1
        for k in keys:
            h = Grid()
            h._Grid__key = k
            cluster1.addGrid(h)
            dstream.grid_list[k] = h
            break

        dstream._D_Stream__adjust_transitional(g)
        self.assertEqual(1, g._Grid__cluster_key)


    def test_initial_clustring(self):
        #1、布置100个不是neighbor的grid，运行函数不会报错
        dstream=D_Stream()
        key='100100'
        for i in range(1,100):
            k=int(key)+3000000
            g=Grid()
            g._Grid__key=str(k)
            dstream.grid_list[k]=g
        dstream._D_Stream__initial_clustring()
        for i in range(1,100):
            k=int(key)+3000000
            grid=dstream.grid_list[k]
            self.assertEqual(grid.clusterKey(),-1)

        #1-2、其中50个是dense，25个transitional，25个sparse，检查50个被分入各自cluster，但是其他50个没有cluster
        dstream = D_Stream()
        key = '100100'
        index=0
        for i in range(1, 100):
            index+=1
            k = int(key) + 3000000
            g = Grid()
            g._Grid__key = str(k)
            dstream.grid_list[k] = g
            if index<50:
                g._Grid__densityStatus=DensityStatus.DENSE
            elif index<75:
                g._Grid__densityStatus = DensityStatus.TRANSITIONAL
            else:
                g._Grid__densityStatus = DensityStatus.SPARSE
        dstream._D_Stream__initial_clustring()
        for i in range(1, 100):
            index+=1
            k = int(key) + 3000000
            grid=dstream.grid_list[k]
            if index < 50:
                self.assertNotEqual(-1,grid.clusterKey())
            else:
                self.assertEqual(-1, grid.clusterKey())


        #2、10个互相隔离的cluster，运行函数后10个cluster没有变化
        dstream = D_Stream()
        index=0
        k='100100'
        for i in range(0,10):
            index+=1
            cluster=Cluster(index)
            dstream.cluster_manager._ClusterManager__cluster_dic[index]=cluster
            dstream.cluster_manager._ClusterManager__cluster_key_index+=1
            key=str(int(k)+5000000)
            g=Grid()
            g._Grid__key=key
            cluster.addGrid(g)
            dstream.grid_list[key]=g
            n_keys=Helper.getNeighborKeys(key)
            for n_key in n_keys:
                n_grid=Grid()
                n_grid._Grid__key=n_key
                cluster.addGrid(n_grid)
                dstream.grid_list[n_keys]=n_grid
        dstream._D_Stream__initial_clustring()
        clusters=dstream.cluster_manager.getAllCluster()
        for cluster in clusters:
            self.assertEqual(7,cluster.size())
        self.assertEqual(10,len(clusters))

        #3、5个cluster，其中1和2接壤，1被2吞并，3和4接壤，4被3吞并、4的邻居有一个transitional的grid 5 ，被4吞并
        dstream = D_Stream()
        cluster=Cluster(1)
        g=Grid()
        g._Grid__key='100100'
        cluster.addGrid(g)
        dstream.grid_list[g.key()]=g
        dstream.cluster_manager._ClusterManager__cluster_dic[1]=cluster
        dstream.cluster_manager._ClusterManager__cluster_key_index+=1

        cluster=Cluster(2)
        g=Grid()
        g._Grid__key='1100100'
        cluster.addGrid(g)
        g1=Grid()
        g1._Grid__key='1100101'
        cluster.addGrid(g1)
        g2 = Grid()
        g2._Grid__key = '1100102'
        cluster.addGrid(g2)
        dstream.grid_list[g.key()] = g
        dstream.grid_list[g1.key()] = g1
        dstream.cluster_manager._ClusterManager__cluster_dic[2] = cluster
        dstream.cluster_manager._ClusterManager__cluster_key_index += 1

        cluster = Cluster(3)
        g = Grid()
        g._Grid__key = '1000100100'
        cluster.addGrid(g)
        g1 = Grid()
        g1._Grid__key = '1001100101'
        cluster.addGrid(g1)
        dstream.grid_list[g.key()] = g
        dstream.grid_list[g1.key()] = g1
        dstream.cluster_manager._ClusterManager__cluster_dic[3] = cluster
        dstream.cluster_manager._ClusterManager__cluster_key_index += 1

        dstream = D_Stream()
        cluster = Cluster(4)
        g = Grid()
        g._Grid__key = '1002100100'
        cluster.addGrid(g)
        dstream.grid_list[g.key()] = g
        dstream.cluster_manager._ClusterManager__cluster_dic[4] = cluster
        dstream.cluster_manager._ClusterManager__cluster_key_index += 1


        h=Grid()
        h._Grid__key='1003100100'
        dstream.grid_list[h.key()] = g

        dstream._D_Stream__initial_clustring()
            #运行函数后，只剩下两个cluster
        clusters=dstream.cluster_manager.getAllCluster()
        self.assertEqual(2,len(clusters))

        cluster2=dstream.cluster_manager.getCluster(2)
        cluster4=dstream.cluster_manager.getCluster(4)
        grids=cluster2.getAllGrids()
        for grid in grids:
            self.assertIn(grid.key(),['100100','1100100','1100100','1100102'])
        grids=cluster4.getAllGrids()
        for grid in grids:
            self.assertIn(grid.key(),['1000100100','1000100100','1002100100','1003100100'])


    def test_do_DStream(self):
        #TODO:两个gap的数据量来做覆盖测试

