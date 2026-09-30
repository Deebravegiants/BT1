# [?] Merge pull request #11075 from ziggie1984/agent/fix-transaction-pagination-overflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-08-14
Source: https://github.com/lightningnetwork/lnd/commit/cfde18d9822aacc0b87ff4d744089939cf438c6b
Type: security-commit

## Details
Merge pull request #11075 from ziggie1984/agent/fix-transaction-pagination-overflow

lnwallet: prevent transaction pagination overflow

## Patch
### docs/release-notes/release-notes-0.20.4.md
```diff
@@ -21,6 +21,11 @@
 
 # Bug Fixes
 
+* [`GetTransactions`
+  pagination](https://github.com/lightningnetwork/lnd/pull/11075) now handles
+  overflowing offset and limit combinations without reaching a slice-bounds
+  panic.
+
 # New Features
 
 ## Functional Enhancements
@@ -56,3 +61,5 @@
 ## Tooling and Documentation
 
 # Contributors (Alphabetical Order)
+
+* Ziggie
```

### docs/release-notes/release-notes-0.21.3.md
```diff
@@ -30,6 +30,11 @@
   first block height when calculating a defensive range boundary, and dense
   first blocks no longer produce zero-block reply prefixes.
 
+* [`GetTransactions`
+  pagination](https://github.com/lightningnetwork/lnd/pull/11075) now handles
+  overflowing offset and limit combinations without reaching a slice-bounds
+  panic.
+
 # New Features
 
 ## Functional Enhancements
@@ -71,3 +76,4 @@
 # Contributors (Alphabetical Order)
 
 * Yong Yu
+* Ziggie
```

### lnwallet/btcwallet/btcwallet.go
```diff
@@ -1554,6 +1554,38 @@ func unminedTransactionsToDetail(
 	return txDetail, nil
 }
 
+// transactionDetailsPage applies the requested offset and limit to a set of
+// transaction details. A zero limit means that all remaining transactions are
+// returned.
+func transactionDetailsPage(txDetails []*lnwallet.TransactionDetail,
+	indexOffset, maxTransactions uint32) ([]*lnwallet.TransactionDetail,
+	uint64, uint64) {
+
+	total := uint64(len(txDetails))
+	first := uint64(indexOffset)
+	if first >= total {
+		return []*lnwallet.TransactionDetail{}, 0, 0
+	}
+
+	end := total
+	if maxTransactions != 0 {
+		// Compare the limit to the remaining count. This avoids adding
+		// caller-controlled values before deciding whether to clamp the
+		// requested end.
+		limit := uint64(maxTransactions)
+		remaining := total - first
+		if limit < remaining {
+			end = first + limit
+		}
+	}
+
+	// Both bounds are no greater than len(txDetails), so these conversions
+	// are safe on both 32-bit and 64-bit platforms.
+	page := txDetails[int(first):int(end)]
+
+	return page, first, end - 1
+}
+
 // ListTransactionDetails returns a list of all transactions which are relevant
 // to the wallet over [startHeight;endHeight]. If start height is greater than
 // end height, the transactions will be retrieved in reverse order. To include
@@ -1607,32 +1639,11 @@ func (b *BtcWallet) ListTransactionDetails(startHeight, endHeight int32,
 		txDetails = append(txDetails, detail)
 	}
 
-	// Return empty transaction list, if offset is more than all
-	// transactions.
-	if int(indexOffset) >= len(txDetails) {
-		txDetails = []*lnwallet.TransactionDetail{}
-
-		return txDetails, 0, 0, nil
-	}
-
-	end := indexOffset + maxTransactions
-
-	// If maxTransactions is set to 0, then we'll return all transactions
-	// starting from the offset.
-	if maxTransactions == 0 {
-		end = uint32(len(txDetails))
-		txDetails = txDetails[indexOffset:end]
-
-		return txDetails, uint64(indexOffset), uint64(end - 1), nil
-	}
-
-	if end > uint32(len(txDetails)) {
-		end = uint32(len(txDetails))
-	}
-
-	txDetails = txDetails[indexOffset:end]
+	page, firstIndex, lastIndex := transactionDetailsPage(
+		txDetails, indexOffset, maxTransactions,
+	)
 
-	return txDetails, uint64(indexOffset), uint64(end - 1), nil
+	return page, firstIndex, lastIndex, nil
 }
 
 // txSubscriptionClient encapsulates the transaction notification client from
```

### lnwallet/btcwallet/btcwallet_test.go
```diff
@@ -1,6 +1,7 @@
 package btcwallet
 
 import (
+	"math"
 	"testing"
 
 	"github.com/btcsuite/btcd/btcjson"
@@ -138,6 +139,79 @@ func TestPreviousOutpoints(t *testing.T) {
 	}
 }
 
+// TestTransactionDetailsPage verifies the bounds returned for transaction
+// pagination, including requests that would overflow with uint32 addition.
+func TestTransactionDetailsPage(t *testing.T) {
+	t.Parallel()
+
+	txDetails := []*lnwallet.TransactionDetail{{}, {}, {}, {}}
+
+	testCases := []struct {
+		name          string
+		offset        uint32
+		limit         uint32
+		expectedPage  []*lnwallet.TransactionDetail
+		expectedFirst uint64
+		expectedLast  uint64
+	}{
+		{
+			name:          "zero limit returns remainder",
+			offset:        1,
+			expectedPage:  txDetails[1:],
+			expectedFirst: 1,
+			expectedLast:  3,
+		},
+		{
+			name:          "limit selects page",
+			offset:        1,
+			limit:         2,
+			expectedPage:  txDetails[1:3],
+			expectedFirst: 1,
+			expectedLast:  2,
+		},
+		{
+			name:          "limit exceeds remainder",
+			offset:        2,
+			limit:         10,
+			expectedPage:  txDetails[2:],
+			expectedFirst: 2,
+			expectedLast:  3,
+		},
+		{
+			name:          "offset plus limit exceeds uint32",
+			offset:        1,
+			limit:         math.MaxUint32,
+			expectedPage:  txDetails[1:],
+			expectedFirst: 1,
+			expectedLast:  3,
+		},
+		{
+			name:         "offset equals transaction count",
+			offset:       uint32(len(txDetails)),
+			limit:        1,
+			expectedPage: []*lnwallet.TransactionDetail{},
+		},
+		{
+			name:         "maximum offset",
+			offset:       math.MaxUint32,
+			limit:        1,
+			expectedPage: []*lnwallet.TransactionDetail{},
+		},
+	}
+
+	for _, testCase := range testCases {
+		t.Run(testCase.name, func(t *testing.T) {
+			page, first, last := transactionDetailsPage(
+				txDetails, testCase.offset, testCase.limit,
+			)
+
+			require.Equal(t, testCase.expectedPage, page)
+			require.Equal(t, testCase.expectedFirst, first)
+			require.Equal(t, testCase.expectedLast, last)
+		})
+	}
+}
+
 // TestCheckMempoolAcceptance asserts the CheckMempoolAcceptance behaves as
 // expected.
 func TestCheckMempoolAcceptance(t *testing.T) {
```
