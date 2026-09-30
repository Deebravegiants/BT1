# [?] fixes state panic ofter trusted reorg (#989)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygonHermez/zkevm-node
Published: 2022-08-03
Source: https://github.com/0xPolygon/zkevm-node/commit/b734d9f11b28ccb1b5bcb153fed78c62cb4ff0ff
Type: security-commit

## Details
fixes state panic ofter trusted reorg (#989)

* fixes

1- decode signature was no needed.
2-synchronizer and sequencer must be running in the same docker instance to avoid problems with the channel.
3-fix in the cli components option

* log

* undo. Sequencer and synchronizer running in different docker instances

## Patch
### cmd/run.go
```diff
@@ -7,7 +7,7 @@ import (
 	"os"
 	"os/signal"
 	"path/filepath"
-	"sort"
+	"strings"
 
 	"github.com/0xPolygonHermez/zkevm-node/aggregator"
 	"github.com/0xPolygonHermez/zkevm-node/config"
@@ -37,12 +37,6 @@ import (
 	"google.golang.org/grpc/credentials/insecure"
 )
 
-// slice contains method
-func contains(s []string, searchTerm string) bool {
-	i := sort.SearchStrings(s, searchTerm)
-	return i < len(s) && s[i] == searchTerm
-}
-
 func start(cliCtx *cli.Context) error {
 	c, err := config.Load(cliCtx)
 	if err != nil {
@@ -70,9 +64,9 @@ func start(cliCtx *cli.Context) error {
 		etherman        *etherman.Client
 	)
 
-	if contains(cliCtx.StringSlice(config.FlagComponents), AGGREGATOR) ||
-		contains(cliCtx.StringSlice(config.FlagComponents), SEQUENCER) ||
-		contains(cliCtx.StringSlice(config.FlagComponents), SYNCHRONIZER) {
+	if strings.Contains(cliCtx.String(config.FlagComponents), AGGREGATOR) ||
+		strings.Contains(cliCtx.String(config.FlagComponents), SEQUENCER) ||
+		strings.Contains(cliCtx.String(config.FlagComponents), SYNCHRONIZER) {
 		var err error
 		etherman, err = newEtherman(*c)
 		if err != nil {
```

### state/helper.go
```diff
@@ -4,13 +4,10 @@ import (
 	"fmt"
 	"math/big"
 	"strconv"
-	"strings"
 
 	"github.com/0xPolygonHermez/zkevm-node/encoding"
-	"github.com/0xPolygonHermez/zkevm-node/etherman/smartcontracts/proofofefficiency"
 	"github.com/0xPolygonHermez/zkevm-node/hex"
 	"github.com/0xPolygonHermez/zkevm-node/log"
-	"github.com/ethereum/go-ethereum/accounts/abi"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/rlp"
 )
@@ -90,32 +87,6 @@ func EncodeUnsignedTransaction(tx types.Transaction) ([]byte, error) {
 
 // DecodeTxs extracts Tansactions for its encoded form
 func DecodeTxs(txsData []byte) ([]types.Transaction, []byte, error) {
-	// The first 4 bytes are the function hash bytes. These bytes has to be ripped.
-	// After that, the unpack method is used to read the call data.
-	// The txs data is a chunk of concatenated rawTx. This rawTx is the encoded tx information in rlp + the signature information (v, r, s).
-	//So, txs data will look like: txRLP+r+s+v+txRLP2+r2+s2+v2
-
-	// Extract coded txs.
-	// Load contract ABI
-	abi, err := abi.JSON(strings.NewReader(proofofefficiency.ProofofefficiencyMetaData.ABI))
-	if err != nil {
-		log.Fatal("error reading smart contract abi: ", err)
-	}
-
-	// Recover Method from signature and ABI
-	method, err := abi.MethodById(txsData[:4])
-	if err != nil {
-		log.Fatal("error getting abi method: ", err)
-	}
-
-	// Unpack method inputs
-	data, err := method.Inputs.Unpack(txsData[4:])
-	if err != nil {
-		log.Fatal("error reading call data: ", err)
-	}
-
-	txsData = data[0].([]byte)
-
 	// Process coded txs
 	var pos int64
 	var txs []types.Transaction
```

### synchronizer/synchronizer.go
```diff
@@ -597,8 +597,8 @@ func (s *ClientSynchronizer) processSequenceBatches(sequencedBatches []etherman.
 			}
 			if !status {
 				// Reset trusted state
-				log.Infof("reorg detected, discarding batches until batchNum %d", batch.BatchNumber)
 				previousBatchNumber := batch.BatchNumber - 1
+				log.Infof("Trusted reorg detected, discarding batches until batchNum %d", previousBatchNumber)
 				err := s.state.ResetTrustedState(s.ctx, previousBatchNumber, dbTx) // This method has to reset the forced batches deleting the batchNumber for higher batchNumbers
 				if err != nil {
 					log.Errorf("error resetting trusted state. BatchNumber: %d, BlockNumber: %d, error: %s", batch.BatchNumber, blockNumber, err.Error())
```
