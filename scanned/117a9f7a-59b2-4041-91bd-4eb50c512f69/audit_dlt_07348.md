# [?] [FAB-16957] Fix nil pointer panic flake in deliver_test (#704)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-02-24
Source: https://github.com/hyperledger/fabric/commit/cc3f58f5e6b70ca69c020949fd7b650dc97dcd52
Type: security-commit

## Details
[FAB-16957] Fix nil pointer panic flake in deliver_test (#704)

* Seems like info.GetStart().GetSpecified() can somehow return nil on
subsequent calls. Let's just assign it before the first nil check and
use it for the rest of the assertion.

Signed-off-by: Danny Cao <dcao@us.ibm.com>

## Patch
### orderer/common/cluster/deliver_test.go
```diff
@@ -32,6 +32,7 @@ import (
 	"github.com/onsi/gomega"
 	"github.com/pkg/errors"
 	"github.com/stretchr/testify/assert"
+	"github.com/stretchr/testify/require"
 	"go.uber.org/zap"
 	"go.uber.org/zap/zapcore"
 	"google.golang.org/grpc"
@@ -271,8 +272,11 @@ func (ds *deliverServer) addExpectProbeAssert() {
 
 func (ds *deliverServer) addExpectPullAssert(seq uint64) {
 	ds.seekAssertions <- func(info *orderer.SeekInfo, _ string) {
-		assert.NotNil(ds.t, info.GetStart().GetSpecified())
-		assert.Equal(ds.t, seq, info.GetStart().GetSpecified().Number)
+		seekPosition := info.GetStart()
+		require.NotNil(ds.t, seekPosition)
+		seekSpecified := seekPosition.GetSpecified()
+		require.NotNil(ds.t, seekSpecified)
+		assert.Equal(ds.t, seq, seekSpecified.Number)
 		assert.Equal(ds.t, info.ErrorResponse, orderer.SeekInfo_BEST_EFFORT)
 	}
 }
```
