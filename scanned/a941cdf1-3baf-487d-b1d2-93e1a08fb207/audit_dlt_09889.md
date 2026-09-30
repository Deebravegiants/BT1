# [?] check db file permission,fix crash when the db file cant be access (#2579)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2021-03-09
Source: https://github.com/iotexproject/iotex-core/commit/f9809474d1f4fee2162f7b5e4bbdfe785c74d5ca
Type: security-commit

## Details
check db file permission,fix crash when the db file cant be access (#2579)

## Patch
### blockchain/blockchain.go
```diff
@@ -194,13 +194,11 @@ func NewBlockchain(cfg config.Config, dao blockdao.BlockDAO, bbf BlockBuilderFac
 		log.L().Panic("Failed to generate prometheus timer factory.", zap.Error(err))
 	}
 	chain.timerFactory = timerFactory
-	// Set block validator
-	if err != nil {
-		log.L().Panic("Failed to get block producer address.", zap.Error(err))
-	}
-	if chain.dao != nil {
-		chain.lifecycle.Add(chain.dao)
+	if chain.dao == nil {
+		log.L().Panic("blockdao is nil")
 	}
+	chain.lifecycle.Add(chain.dao)
+
 	return chain
 }
 
```

### blockchain/blockdao/blockdao.go
```diff
@@ -75,6 +75,7 @@ type (
 func NewBlockDAO(indexers []BlockIndexer, cfg config.DB) BlockDAO {
 	blkStore, err := filedao.NewFileDAO(cfg)
 	if err != nil {
+		log.L().Fatal(err.Error(), zap.Any("cfg", cfg))
 		return nil
 	}
 	return createBlockDAO(blkStore, indexers, cfg)
```

### blockchain/filedao/filedao.go
```diff
@@ -37,6 +37,7 @@ var (
 // vars
 var (
 	ErrFileNotExist     = errors.New("file does not exist")
+	ErrFileCantAccess   = errors.New("cannot access file")
 	ErrFileInvalid      = errors.New("file format is not valid")
 	ErrNotSupported     = errors.New("feature not supported")
 	ErrAlreadyExist     = errors.New("block already exist")
@@ -84,7 +85,7 @@ type (
 // NewFileDAO creates an instance of FileDAO
 func NewFileDAO(cfg config.DB) (FileDAO, error) {
 	header, err := checkMasterChainDBFile(cfg.DbPath)
-	if err == ErrFileInvalid {
+	if err == ErrFileInvalid || err == ErrFileCantAccess {
 		return nil, err
 	}
 
```

### blockchain/filedao/filedao_util.go
```diff
@@ -14,6 +14,7 @@ import (
 	"path"
 	"strconv"
 	"strings"
+	"syscall"
 
 	"github.com/iotexproject/go-pkgs/hash"
 
@@ -23,7 +24,7 @@ import (
 
 func checkMasterChainDBFile(defaultName string) (*FileHeader, error) {
 	h, err := readFileHeader(defaultName, FileAll)
-	if err == ErrFileNotExist || err == ErrFileInvalid {
+	if err == ErrFileNotExist || err == ErrFileInvalid || err == ErrFileCantAccess {
 		return nil, err
 	}
 
@@ -39,10 +40,8 @@ func checkMasterChainDBFile(defaultName string) (*FileHeader, error) {
 }
 
 func readFileHeader(filename, fileType string) (*FileHeader, error) {
-	size, exist := fileExists(filename)
-	if !exist || size == 0 {
-		// default chain db file does not exist
-		return nil, ErrFileNotExist
+	if err := fileExists(filename); err != nil {
+		return nil, err
 	}
 
 	file := db.NewBoltDB(config.DB{DbPath: filename, NumRetries: 3})
@@ -74,12 +73,16 @@ func readFileHeader(filename, fileType string) (*FileHeader, error) {
 	}
 }
 
-func fileExists(name string) (int64, bool) {
+func fileExists(name string) error {
 	info, err := os.Stat(name)
-	if err != nil || info.IsDir() {
-		return 0, false
+	if err != nil || info.IsDir() || info.Size() == 0 {
+		return ErrFileNotExist
+	}
+	err = syscall.Access(name, syscall.O_RDWR)
+	if err != nil {
+		return ErrFileCantAccess
 	}
-	return info.Size(), true
+	return nil
 }
 
 func checkAuxFiles(filename, fileType string) (uint64, []string) {
```
