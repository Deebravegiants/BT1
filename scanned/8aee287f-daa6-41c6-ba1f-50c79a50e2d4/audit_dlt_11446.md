# [?] offchain - prevent panic and remove unused param (#457)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-02-13
Source: https://github.com/smartcontractkit/ccip/commit/93c4837bebdd06bacec51c6eedcea33765840dc9
Type: security-commit

## Details
offchain - prevent panic and remove unused param (#457)

## Motivation


## Solution

## Patch
### core/services/ocr2/plugins/ccip/ccipexec/batching.go
```diff
@@ -2,6 +2,7 @@ package ccipexec
 
 import (
 	"context"
+	"fmt"
 
 	"github.com/pkg/errors"
 
@@ -23,6 +24,11 @@ func getProofData(
 	if err != nil {
 		return nil, nil, nil, err
 	}
+
+	if err1 := validateSendRequests(sendReqs, interval); err1 != nil {
+		return nil, nil, nil, err1
+	}
+
 	leaves = make([][32]byte, 0, len(sendReqs))
 	for _, req := range sendReqs {
 		leaves = append(leaves, req.Data.Hash)
@@ -34,9 +40,33 @@ func getProofData(
 	return sendReqs, leaves, tree, nil
 }
 
+func validateSendRequests(sendReqs []ccipdata.Event[internal.EVM2EVMMessage], interval ccipdata.CommitStoreInterval) error {
+	if len(sendReqs) == 0 {
+		return fmt.Errorf("could not find any requests in the provided interval %v", interval)
+	}
+
+	gotInterval := ccipdata.CommitStoreInterval{
+		Min: sendReqs[0].Data.SequenceNumber,
+		Max: sendReqs[0].Data.SequenceNumber,
+	}
+
+	for _, req := range sendReqs[1:] {
+		if req.Data.SequenceNumber < gotInterval.Min {
+			gotInterval.Min = req.Data.SequenceNumber
+		}
+		if req.Data.SequenceNumber > gotInterval.Max {
+			gotInterval.Max = req.Data.SequenceNumber
+		}
+	}
+
+	if (gotInterval.Min != interval.Min) || (gotInterval.Max != interval.Max) {
+		return fmt.Errorf("interval %v is not the expected %v", gotInterval, interval)
+	}
+	return nil
+}
+
 func buildExecutionReportForMessages(
 	msgsInRoot []ccipdata.Event[internal.EVM2EVMMessage],
-	leaves [][32]byte,
 	tree *merklemulti.Tree[[32]byte],
 	commitInterval ccipdata.CommitStoreInterval,
 	observedMessages []ccip.ObservedMessage,
@@ -50,6 +80,11 @@ func buildExecutionReportForMessages(
 			continue
 		}
 		innerIdx := int(observedMessage.SeqNr - commitInterval.Min)
+		if innerIdx >= len(msgsInRoot) || innerIdx < 0 {
+			return ccipdata.ExecReport{}, fmt.Errorf("invalid inneridx SeqNr=%d IntervalMin=%d msgsInRoot=%d",
+				observedMessage.SeqNr, commitInterval.Min, len(msgsInRoot))
+		}
+
 		messages = append(messages, msgsInRoot[innerIdx].Data)
 		offchainTokenData = append(offchainTokenData, observedMessage.TokenData)
 		innerIdxs = append(innerIdxs, innerIdx)
```

### core/services/ocr2/plugins/ccip/ccipexec/batching_test.go
```diff
@@ -0,0 +1,67 @@
+package ccipexec
+
+import (
+	"testing"
+
+	"github.com/stretchr/testify/assert"
+
+	"github.com/smartcontractkit/chainlink/v2/core/services/ocr2/plugins/ccip/internal"
+	"github.com/smartcontractkit/chainlink/v2/core/services/ocr2/plugins/ccip/internal/ccipdata"
+)
+
+func Test_validateSendRequests(t *testing.T) {
+	testCases := []struct {
+		name             string
+		seqNums          []uint64
+		providedInterval ccipdata.CommitStoreInterval
+		expErr           bool
+	}{
+		{
+			name:             "zero interval no seq nums",
+			seqNums:          nil,
+			providedInterval: ccipdata.CommitStoreInterval{Min: 0, Max: 0},
+			expErr:           true,
+		},
+		{
+			name:             "exp 1 seq num got none",
+			seqNums:          nil,
+			providedInterval: ccipdata.CommitStoreInterval{Min: 1, Max: 1},
+			expErr:           true,
+		},
+		{
+			name:             "exp 10 seq num got none",
+			seqNums:          nil,
+			providedInterval: ccipdata.CommitStoreInterval{Min: 1, Max: 10},
+			expErr:           true,
+		},
+		{
+			name:             "got 1 seq num as expected",
+			seqNums:          []uint64{1},
+			providedInterval: ccipdata.CommitStoreInterval{Min: 1, Max: 1},
+			expErr:           false,
+		},
+		{
+			name:             "got 5 seq num as expected",
+			seqNums:          []uint64{11, 12, 13, 14, 15},
+			providedInterval: ccipdata.CommitStoreInterval{Min: 11, Max: 15},
+			expErr:           false,
+		},
+	}
+
+	for _, tc := range testCases {
+		t.Run(tc.name, func(t *testing.T) {
+			sendReqs := make([]ccipdata.Event[internal.EVM2EVMMessage], 0, len(tc.seqNums))
+			for _, seqNum := range tc.seqNums {
+				sendReqs = append(sendReqs, ccipdata.Event[internal.EVM2EVMMessage]{
+					Data: internal.EVM2EVMMessage{SequenceNumber: seqNum},
+				})
+			}
+			err := validateSendRequests(sendReqs, tc.providedInterval)
+			if tc.expErr {
+				assert.Error(t, err)
+				return
+			}
+			assert.NoError(t, err)
+		})
+	}
+}
```

### core/services/ocr2/plugins/ccip/ccipexec/ocr2.go
```diff
@@ -704,14 +704,14 @@ func (r *ExecutionReportingPlugin) buildReport(ctx context.Context, lggr logger.
 	}
 	lggr.Infow("Building execution report", "observations", observedMessages, "merkleRoot", hexutil.Encode(commitReport.MerkleRoot[:]), "report", commitReport)
 
-	sendReqsInRoot, leaves, tree, err := getProofData(ctx, r.onRampReader, commitReport.Interval)
+	sendReqsInRoot, _, tree, err := getProofData(ctx, r.onRampReader, commitReport.Interval)
 	if err != nil {
 		return nil, err
 	}
 
 	// cap messages which fits MaxExecutionReportLength (after serialized)
 	capped := sort.Search(len(observedMessages), func(i int) bool {
-		report, err2 := buildExecutionReportForMessages(sendReqsInRoot, leaves, tree, commitReport.Interval, observedMessages[:i+1])
+		report, err2 := buildExecutionReportForMessages(sendReqsInRoot, tree, commitReport.Interval, observedMessages[:i+1])
 		if err2 != nil {
 			r.lggr.Errorw("build execution report", "err", err2)
 			return false
@@ -724,11 +724,8 @@ func (r *ExecutionReportingPlugin) buildReport(ctx context.Context, lggr logger.
 		}
 		return len(encoded) > MaxExecutionReportLength
 	})
-	if err != nil {
-		return nil, err
-	}
 
-	execReport, err := buildExecutionReportForMessages(sendReqsInRoot, leaves, tree, commitReport.Interval, observedMessages[:capped])
+	execReport, err := buildExecutionReportForMessages(sendReqsInRoot, tree, commitReport.Interval, observedMessages[:capped])
 	if err != nil {
 		return nil, err
 	}
```

### core/services/ocr2/plugins/ccip/internal/ccipdata/onramp_reader.go
```diff
@@ -34,6 +34,8 @@ type OnRampDynamicConfig struct {
 //go:generate mockery --quiet --name OnRampReader --filename onramp_reader_mock.go --case=underscore
 type OnRampReader interface {
 	// GetSendRequestsBetweenSeqNums returns all the finalized message send requests in the provided sequence numbers range (inclusive).
+	// If some requests do not exist in the provided sequence numbers range they will not be part of the response.
+	// It's the responsibility of the caller to validate whether all the requests exist or not.
 	GetSendRequestsBetweenSeqNums(ctx context.Context, seqNumMin, seqNumMax uint64, finalized bool) ([]Event[internal.EVM2EVMMessage], error)
 	// Get router configured in the onRamp
 	RouterAddress() (common.Address, error)
```
