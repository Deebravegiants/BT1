# [?] sqldb: bump modernc.org/sqlite to 1.29.10 which fixes init data race

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2024-06-21
Source: https://github.com/lightningnetwork/lnd/commit/892561f8f032a477f54b87bd45c6a8851fa5d751
Type: security-commit

## Details
sqldb: bump modernc.org/sqlite to 1.29.10 which fixes init data race

Tracking issue: https://gitlab.com/cznic/sqlite/-/issues/180

## Patch
### go.mod
```diff
@@ -186,7 +186,7 @@ require (
 	modernc.org/libc v1.49.3 // indirect
 	modernc.org/mathutil v1.6.0 // indirect
 	modernc.org/memory v1.8.0 // indirect
-	modernc.org/sqlite v1.29.8 // indirect
+	modernc.org/sqlite v1.29.10 // indirect
 	modernc.org/strutil v1.2.0 // indirect
 	modernc.org/token v1.1.0 // indirect
 	sigs.k8s.io/yaml v1.2.0 // indirect
@@ -203,6 +203,9 @@ replace github.com/gogo/protobuf => github.com/gogo/protobuf v1.3.2
 // allows us to specify that as an option.
 replace google.golang.org/protobuf => github.com/lightninglabs/protobuf-go-hex-display v1.30.0-hex-display
 
+// Temporary replace until the next version of sqldb is tagged.
+replace github.com/lightningnetwork/lnd/sqldb => ./sqldb
+
 // If you change this please also update .github/pull_request_template.md and
 // docs/INSTALL.md.
 go 1.21.4
```

### go.sum
```diff
@@ -456,8 +456,6 @@ github.com/lightningnetwork/lnd/kvdb v1.4.8 h1:xH0a5Vi1yrcZ5BEeF2ba3vlKBRxrL9uYX
 github.com/lightningnetwork/lnd/kvdb v1.4.8/go.mod h1:J2diNABOoII9UrMnxXS5w7vZwP7CA1CStrl8MnIrb3A=
 github.com/lightningnetwork/lnd/queue v1.1.1 h1:99ovBlpM9B0FRCGYJo6RSFDlt8/vOkQQZznVb18iNMI=
 github.com/lightningnetwork/lnd/queue v1.1.1/go.mod h1:7A6nC1Qrm32FHuhx/mi1cieAiBZo5O6l8IBIoQxvkz4=
-github.com/lightningnetwork/lnd/sqldb v1.0.2 h1:PfuYzScYMD9/QonKo/QvgsbXfTnH5DfldIimkfdW4Bk=
-github.com/lightningnetwork/lnd/sqldb v1.0.2/go.mod h1:V2Xl6JNWLTKE97WJnwfs0d0TYJdIQTqK8/3aAwkd3qI=
 github.com/lightningnetwork/lnd/ticker v1.1.1 h1:J/b6N2hibFtC7JLV77ULQp++QLtCwT6ijJlbdiZFbSM=
 github.com/lightningnetwork/lnd/ticker v1.1.1/go.mod h1:waPTRAAcwtu7Ji3+3k+u/xH5GHovTsCoSVpho0KDvdA=
 github.com/lightningnetwork/lnd/tlv v1.2.3 h1:If5ibokA/UoCBGuCKaY6Vn2SJU0l9uAbehCnhTZjEP8=
@@ -479,8 +477,6 @@ github.com/mattn/go-isatty v0.0.20 h1:xfD0iDuEKnDkl03q4limB+vH+GxLEtL/jb4xVJSWWE
 github.com/mattn/go-isatty v0.0.20/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
 github.com/mattn/go-runewidth v0.0.13 h1:lTGmDsbAYt5DmK6OnoV7EuIF1wEIFAcxld6ypU4OSgU=
 github.com/mattn/go-runewidth v0.0.13/go.mod h1:Jdepj2loyihRzMpdS35Xk/zdY8IAYHsh153qUoGf23w=
-github.com/mattn/go-sqlite3 v1.14.22 h1:2gZY6PC6kBnID23Tichd1K+Z0oS6nE/XwU+Vz/5o4kU=
-github.com/mattn/go-sqlite3 v1.14.22/go.mod h1:Uh1q+B4BYcTPb+yiD3kU8Ct7aC0hY9fxUwlHK0RXw+Y=
 github.com/matttproud/golang_protobuf_extensions v1.0.1 h1:4hp9jkHxhMHkqkrB3Ix0jegS5sx/RkqARlsWZ6pIwiU=
 github.com/matttproud/golang_protobuf_extensions v1.0.1/go.mod h1:D8He9yQNgCq6Z5Ld7szi9bcBfOoFv/3dc6xSMkL2PC0=
 github.com/miekg/dns v1.1.43 h1:JKfpVSCB84vrAmHzyrsxB5NAr5kLoMXZArPSw7Qlgyg=
@@ -1064,8 +1060,8 @@ modernc.org/opt v0.1.3 h1:3XOZf2yznlhC+ibLltsDGzABUGVx8J6pnFMS3E4dcq4=
 modernc.org/opt v0.1.3/go.mod h1:WdSiB5evDcignE70guQKxYUl14mgWtbClRi5wmkkTX0=
 modernc.org/sortutil v1.2.0 h1:jQiD3PfS2REGJNzNCMMaLSp/wdMNieTbKX920Cqdgqc=
 modernc.org/sortutil v1.2.0/go.mod h1:TKU2s7kJMf1AE84OoiGppNHJwvB753OYfNl2WRb++Ss=
-modernc.org/sqlite v1.29.8 h1:nGKglNx9K5v0As+zF0/Gcl1kMkmaU1XynYyq92PbsC8=
-modernc.org/sqlite v1.29.8/go.mod h1:lQPm27iqa4UNZpmr4Aor0MH0HkCLbt1huYDfWylLZFk=
+modernc.org/sqlite v1.29.10 h1:3u93dz83myFnMilBGCOLbr+HjklS6+5rJLx4q86RDAg=
+modernc.org/sqlite v1.29.10/go.mod h1:ItX2a1OVGgNsFh6Dv60JQvGfJfTPHPVpV6DF59akYOA=
 modernc.org/strutil v1.2.0 h1:agBi9dp1I+eOnxXeiZawM8F4LawKv4NzGWSaLfyeNZA=
 modernc.org/strutil v1.2.0/go.mod h1:/mdcBmfOibveCTBxUl5B5l6W+TTH1FXPLHZE6bTosX0=
 modernc.org/token v1.1.0 h1:Xl7Ap9dKaEs5kLoOQeQmPWevfnk/DM5qcLcYlA8ys6Y=
```

### invoices/invoiceregistry_test.go
```diff
@@ -6,7 +6,6 @@ import (
 	"database/sql"
 	"fmt"
 	"math"
-	"sync"
 	"testing"
 	"testing/quick"
 	"time"
@@ -24,12 +23,6 @@ import (
 	"github.com/stretchr/testify/require"
 )
 
-// sqliteConstructorMu is used to ensure that only one thread can call the
-// sqldb.NewTestSqliteDB constructor at a time. This is a temporary workaround
-// that can be removed once this race condition in the sqlite repo is resolved:
-// https://gitlab.com/cznic/sqlite/-/issues/180
-var sqliteConstructorMu sync.Mutex
-
 // TestInvoiceRegistry is a master test which encompasses all tests using an
 // InvoiceDB instance. The purpose of this test is to be able to run all tests
 // with a custom DB instance, so that we can test the same logic with different
@@ -137,9 +130,7 @@ func TestInvoiceRegistry(t *testing.T) {
 
 		var db *sqldb.BaseDB
 		if sqlite {
-			sqliteConstructorMu.Lock()
 			db = sqldb.NewTestSqliteDB(t).BaseDB
-			sqliteConstructorMu.Unlock()
 		} else {
 			db = sqldb.NewTestPostgresDB(t, pgFixture).BaseDB
 		}
```

### invoices/invoices_test.go
```diff
@@ -234,9 +234,7 @@ func TestInvoices(t *testing.T) {
 	makeSQLDB := func(t *testing.T, sqlite bool) invpkg.InvoiceDB {
 		var db *sqldb.BaseDB
 		if sqlite {
-			sqliteConstructorMu.Lock()
 			db = sqldb.NewTestSqliteDB(t).BaseDB
-			sqliteConstructorMu.Unlock()
 		} else {
 			db = sqldb.NewTestPostgresDB(t, pgFixture).BaseDB
 		}
```

### sqldb/go.mod
```diff
@@ -11,7 +11,7 @@ require (
 	github.com/ory/dockertest/v3 v3.10.0
 	github.com/stretchr/testify v1.9.0
 	golang.org/x/exp v0.0.0-20240325151524-a685a6edb6d8
-	modernc.org/sqlite v1.29.8
+	modernc.org/sqlite v1.29.10
 )
 
 require (
```

### sqldb/go.sum
```diff
@@ -92,8 +92,6 @@ github.com/lib/pq v1.10.9 h1:YXG7RB+JIjhP29X+OtkiDnYaXQwpS4JEWq7dtCCRUEw=
 github.com/lib/pq v1.10.9/go.mod h1:AlVN5x4E4T544tWzH6hKfbfQvm3HdbOxrmggDNAPY9o=
 github.com/mattn/go-isatty v0.0.20 h1:xfD0iDuEKnDkl03q4limB+vH+GxLEtL/jb4xVJSWWEY=
 github.com/mattn/go-isatty v0.0.20/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
-github.com/mattn/go-sqlite3 v1.14.22 h1:2gZY6PC6kBnID23Tichd1K+Z0oS6nE/XwU+Vz/5o4kU=
-github.com/mattn/go-sqlite3 v1.14.22/go.mod h1:Uh1q+B4BYcTPb+yiD3kU8Ct7aC0hY9fxUwlHK0RXw+Y=
 github.com/mitchellh/mapstructure v1.4.1 h1:CpVNEelQCZBooIPDn+AR3NpivK/TIKU8bDxdASFVQag=
 github.com/mitchellh/mapstructure v1.4.1/go.mod h1:bFUtVrKA4DC2yAKiSyO/QUcy7e+RRV2QTWOzhPopBRo=
 github.com/moby/sys/mountinfo v0.5.0/go.mod h1:3bMD3Rg+zkqx8MRYPi7Pyb0Ie97QEBmdxbhnCLlSvSU=
@@ -233,8 +231,8 @@ modernc.org/opt v0.1.3 h1:3XOZf2yznlhC+ibLltsDGzABUGVx8J6pnFMS3E4dcq4=
 modernc.org/opt v0.1.3/go.mod h1:WdSiB5evDcignE70guQKxYUl14mgWtbClRi5wmkkTX0=
 modernc.org/sortutil v1.2.0 h1:jQiD3PfS2REGJNzNCMMaLSp/wdMNieTbKX920Cqdgqc=
 modernc.org/sortutil v1.2.0/go.mod h1:TKU2s7kJMf1AE84OoiGppNHJwvB753OYfNl2WRb++Ss=
-modernc.org/sqlite v1.29.8 h1:nGKglNx9K5v0As+zF0/Gcl1kMkmaU1XynYyq92PbsC8=
-modernc.org/sqlite v1.29.8/go.mod h1:lQPm27iqa4UNZpmr4Aor0MH0HkCLbt1huYDfWylLZFk=
+modernc.org/sqlite v1.29.10 h1:3u93dz83myFnMilBGCOLbr+HjklS6+5rJLx4q86RDAg=
+modernc.org/sqlite v1.29.10/go.mod h1:ItX2a1OVGgNsFh6Dv60JQvGfJfTPHPVpV6DF59akYOA=
 modernc.org/strutil v1.2.0 h1:agBi9dp1I+eOnxXeiZawM8F4LawKv4NzGWSaLfyeNZA=
 modernc.org/strutil v1.2.0/go.mod h1:/mdcBmfOibveCTBxUl5B5l6W+TTH1FXPLHZE6bTosX0=
 modernc.org/token v1.1.0 h1:Xl7Ap9dKaEs5kLoOQeQmPWevfnk/DM5qcLcYlA8ys6Y=
```
