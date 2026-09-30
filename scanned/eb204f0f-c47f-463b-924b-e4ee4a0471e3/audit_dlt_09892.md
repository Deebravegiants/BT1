# [?] fix blockdao deadlock bug (#2065)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2020-03-25
Source: https://github.com/iotexproject/iotex-core/commit/aa55104257bc6f0711e754d1b119a6145798f611
Type: security-commit

## Details
fix blockdao deadlock bug (#2065)

1. fix blockdao deadlock issue 
2. fix GetTipDB() index issue

## Patch
### blockchain/blockdao/blockdao.go
```diff
@@ -88,8 +88,6 @@ type (
 		GetReceipts(uint64) ([]*action.Receipt, error)
 		PutBlock(*block.Block) error
 		DeleteBlockToTarget(uint64) error
-		IndexFile(uint64, []byte) error
-		GetFileIndex(uint64) ([]byte, error)
 		KVStore() db.KVStore
 		HeaderByHeight(uint64) (*block.Header, error)
 		FooterByHeight(uint64) (*block.Footer, error)
@@ -327,8 +325,6 @@ func (dao *blockDAO) GetReceipts(blkHeight uint64) ([]*action.Receipt, error) {
 
 func (dao *blockDAO) PutBlock(blk *block.Block) error {
 	err := func() error {
-		dao.mutex.Lock()
-		defer dao.mutex.Unlock()
 		if err := dao.putBlock(blk); err != nil {
 			return err
 		}
@@ -349,8 +345,6 @@ func (dao *blockDAO) PutBlock(blk *block.Block) error {
 }
 
 func (dao *blockDAO) DeleteBlockToTarget(targetHeight uint64) error {
-	dao.mutex.Lock()
-	defer dao.mutex.Unlock()
 	tipHeight, err := dao.getTipHeight()
 	if err != nil {
 		return err
@@ -381,7 +375,7 @@ func (dao *blockDAO) DeleteBlockToTarget(targetHeight uint64) error {
 	return nil
 }
 
-func (dao *blockDAO) IndexFile(height uint64, index []byte) error {
+func (dao *blockDAO) indexFile(height uint64, index []byte) error {
 	dao.mutex.Lock()
 	defer dao.mutex.Unlock()
 
@@ -395,8 +389,8 @@ func (dao *blockDAO) IndexFile(height uint64, index []byte) error {
 	return dao.htf.Insert(height, index)
 }
 
-// GetFileIndex return the db filename
-func (dao *blockDAO) GetFileIndex(height uint64) ([]byte, error) {
+// getFileIndex return the db filename
+func (dao *blockDAO) getFileIndex(height uint64) ([]byte, error) {
 	dao.mutex.RLock()
 	defer dao.mutex.RUnlock()
 
@@ -780,7 +774,7 @@ func (dao *blockDAO) getTopDB(blkHeight uint64) (kvStore db.KVStore, index uint6
 	dat, err := os.Stat(longFileName)
 	if err != nil && os.IsNotExist(err) {
 		// index the height --> file index mapping
-		if err = dao.IndexFile(blkHeight, byteutil.Uint64ToBytesBigEndian(topIndex)); err != nil {
+		if err = dao.indexFile(blkHeight, byteutil.Uint64ToBytesBigEndian(topIndex)); err != nil {
 			return
 		}
 		// db file does not exist, create it
@@ -795,7 +789,7 @@ func (dao *blockDAO) getTopDB(blkHeight uint64) (kvStore db.KVStore, index uint6
 		kvStore, index, err = dao.openDB(topIndex + 1)
 		dao.topIndex.Store(index)
 		// index the height --> file index mapping
-		err = dao.IndexFile(blkHeight, byteutil.Uint64ToBytesBigEndian(topIndex))
+		err = dao.indexFile(blkHeight, byteutil.Uint64ToBytesBigEndian(index))
 		return
 	}
 	// db exist,need load from kvStores
@@ -820,7 +814,7 @@ func (dao *blockDAO) getDBFromHeight(blkHeight uint64) (kvStore db.KVStore, inde
 		return dao.kvStore, 0, nil
 	}
 	// get file index
-	value, err := dao.GetFileIndex(blkHeight)
+	value, err := dao.getFileIndex(blkHeight)
 	if err != nil {
 		return
 	}
@@ -873,12 +867,12 @@ func (dao *blockDAO) openDB(idx uint64) (kvStore db.KVStore, index uint64, err e
 	if idx == 0 {
 		return dao.kvStore, 0, nil
 	}
-	dao.mutex.Lock()
-	defer dao.mutex.Unlock()
 	cfg := dao.cfg
 	model, _ := getFileNameAndDir(cfg.DbPath)
 	name := model + fmt.Sprintf("-%08d", idx) + ".db"
 
+	dao.mutex.Lock()
+	defer dao.mutex.Unlock()
 	// open or create this db file
 	cfg.DbPath = path.Dir(cfg.DbPath) + "/" + name
 	kvStore = db.NewBoltDB(cfg)
```

### test/mock/mock_blockdao/mock_blockdao.go
```diff
@@ -258,35 +258,6 @@ func (mr *MockBlockDAOMockRecorder) DeleteBlockToTarget(arg0 interface{}) *gomoc
 	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "DeleteBlockToTarget", reflect.TypeOf((*MockBlockDAO)(nil).DeleteBlockToTarget), arg0)
 }
 
-// IndexFile mocks base method
-func (m *MockBlockDAO) IndexFile(arg0 uint64, arg1 []byte) error {
-	m.ctrl.T.Helper()
-	ret := m.ctrl.Call(m, "IndexFile", arg0, arg1)
-	ret0, _ := ret[0].(error)
-	return ret0
-}
-
-// IndexFile indicates an expected call of IndexFile
-func (mr *MockBlockDAOMockRecorder) IndexFile(arg0, arg1 interface{}) *gomock.Call {
-	mr.mock.ctrl.T.Helper()
-	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "IndexFile", reflect.TypeOf((*MockBlockDAO)(nil).IndexFile), arg0, arg1)
-}
-
-// GetFileIndex mocks base method
-func (m *MockBlockDAO) GetFileIndex(arg0 uint64) ([]byte, error) {
-	m.ctrl.T.Helper()
-	ret := m.ctrl.Call(m, "GetFileIndex", arg0)
-	ret0, _ := ret[0].([]byte)
-	ret1, _ := ret[1].(error)
-	return ret0, ret1
-}
-
-// GetFileIndex indicates an expected call of GetFileIndex
-func (mr *MockBlockDAOMockRecorder) GetFileIndex(arg0 interface{}) *gomock.Call {
-	mr.mock.ctrl.T.Helper()
-	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "GetFileIndex", reflect.TypeOf((*MockBlockDAO)(nil).GetFileIndex), arg0)
-}
-
 // KVStore mocks base method
 func (m *MockBlockDAO) KVStore() db.KVStore {
 	m.ctrl.T.Helper()
```
