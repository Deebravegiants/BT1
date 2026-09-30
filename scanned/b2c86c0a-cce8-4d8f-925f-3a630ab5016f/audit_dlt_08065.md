# [?] vendor: fix leveldb crash when bigger than 1 TiB

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-05-01
Source: https://github.com/celo-org/celo-blockchain/commit/a1949d0788ecb1d890677bdd26c0e711ddf639b2
Type: security-commit

## Details
vendor: fix leveldb crash when bigger than 1 TiB

## Patch
### vendor/github.com/syndtr/goleveldb/leveldb/storage/mem_storage.go
```diff
@@ -12,7 +12,11 @@ import (
 	"sync"
 )
 
-const typeShift = 3
+const typeShift = 4
+
+// Verify at compile-time that typeShift is large enough to cover all FileType
+// values by confirming that 0 == 0.
+var _ [0]struct{} = [TypeAll >> typeShift]struct{}{}
 
 type memStorageLock struct {
 	ms *memStorage
@@ -143,7 +147,7 @@ func (ms *memStorage) Remove(fd FileDesc) error {
 }
 
 func (ms *memStorage) Rename(oldfd, newfd FileDesc) error {
-	if FileDescOk(oldfd) || FileDescOk(newfd) {
+	if !FileDescOk(oldfd) || !FileDescOk(newfd) {
 		return ErrInvalidFile
 	}
 	if oldfd == newfd {
```

### vendor/github.com/syndtr/goleveldb/leveldb/util.go
```diff
@@ -20,7 +20,7 @@ func shorten(str string) string {
 	return str[:3] + ".." + str[len(str)-3:]
 }
 
-var bunits = [...]string{"", "Ki", "Mi", "Gi"}
+var bunits = [...]string{"", "Ki", "Mi", "Gi", "Ti"}
 
 func shortenb(bytes int) string {
 	i := 0
```

### vendor/vendor.json
```diff
@@ -418,76 +418,76 @@
 			"revisionTime": "2017-07-05T02:17:15Z"
 		},
 		{
-			"checksumSHA1": "3QsnhPTXGytTbW3uDvQLgSo9s9M=",
+			"checksumSHA1": "k13cCuMJO7+KhR8ZXx5oUqDKGQA=",
 			"path": "github.com/syndtr/goleveldb/leveldb",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "EKIow7XkgNdWvR/982ffIZxKG8Y=",
 			"path": "github.com/syndtr/goleveldb/leveldb/cache",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "5KPgnvCPlR0ysDAqo6jApzRQ3tw=",
 			"path": "github.com/syndtr/goleveldb/leveldb/comparer",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "1DRAxdlWzS4U0xKN/yQ/fdNN7f0=",
 			"path": "github.com/syndtr/goleveldb/leveldb/errors",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "eqKeD6DS7eNCtxVYZEHHRKkyZrw=",
 			"path": "github.com/syndtr/goleveldb/leveldb/filter",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "weSsccMav4BCerDpSLzh3mMxAYo=",
 			"path": "github.com/syndtr/goleveldb/leveldb/iterator",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "gJY7bRpELtO0PJpZXgPQ2BYFJ88=",
 			"path": "github.com/syndtr/goleveldb/leveldb/journal",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "MtYY1b2234y/MlS+djL8tXVAcQs=",
 			"path": "github.com/syndtr/goleveldb/leveldb/memdb",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "UmQeotV+m8/FduKEfLOhjdp18rs=",
 			"path": "github.com/syndtr/goleveldb/leveldb/opt",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
-			"checksumSHA1": "QCSae2ub87f8awH+PKMpd8ZYOtg=",
+			"checksumSHA1": "7H3fa12T7WoMAeXq1+qG5O7LD0w=",
 			"path": "github.com/syndtr/goleveldb/leveldb/storage",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "gWFPMz8OQeul0t54RM66yMTX49g=",
 			"path": "github.com/syndtr/goleveldb/leveldb/table",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "V/Dh7NV0/fy/5jX1KaAjmGcNbzI=",
 			"path": "github.com/syndtr/goleveldb/leveldb/util",
-			"revision": "169b1b37be738edb2813dab48c97a549bcf99bb5",
-			"revisionTime": "2018-03-07T11:33:52Z"
+			"revision": "ae970a0732be3a1f5311da86118d37b9f4bd2a5a",
+			"revisionTime": "2018-05-02T07:23:49Z"
 		},
 		{
 			"checksumSHA1": "TT1rac6kpQp2vz24m5yDGUNQ/QQ=",
```
