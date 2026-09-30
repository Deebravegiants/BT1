# [?] chg: use decimals over hex and fix overflow

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/heimdall
Published: 2024-11-13
Source: https://github.com/0xPolygon/heimdall/commit/dcc009745d5985770b03d8b6b0aa5ab48fe46057
Type: security-commit

## Details
chg: use decimals over hex and fix overflow

## Patch
### bor/client/grpc/grpc_util_test.go
```diff
@@ -0,0 +1,54 @@
+package grpc
+
+import (
+	"math/big"
+	"testing"
+
+	"github.com/stretchr/testify/assert"
+)
+
+func TestToBlockNumArg(t *testing.T) {
+	tests := []struct {
+		name     string
+		input    *big.Int
+		expected string
+	}{
+		{
+			name:     "Nil input",
+			input:    nil,
+			expected: "latest",
+		},
+		{
+			name:     "Positive number",
+			input:    big.NewInt(12345),
+			expected: "12345",
+		},
+		{
+			name:     "Zero",
+			input:    big.NewInt(0),
+			expected: "0",
+		},
+		{
+			name:     "Negative number",
+			input:    big.NewInt(-1),
+			expected: "pending",
+		},
+		{
+			name:     "Large negative number",
+			input:    big.NewInt(-1234567890),
+			expected: "<invalid -1234567890>",
+		},
+		{
+			name:     "Large number",
+			input:    big.NewInt(99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999),
+			expected: "<invalid 99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999>",
+		},
+	}
+
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			result := ToBlockNumArg(tt.input)
+			assert.Equal(t, tt.expected, result)
+		})
+	}
+}
```

### bor/client/grpc/query.go
```diff
@@ -6,7 +6,7 @@ import (
 	"math/big"
 
 	"github.com/ethereum/go-ethereum/common"
-	"github.com/ethereum/go-ethereum/common/hexutil"
+	"github.com/ethereum/go-ethereum/common/math"
 	ethTypes "github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/log"
 	"github.com/ethereum/go-ethereum/rpc"
@@ -57,7 +57,11 @@ func (h *BorGRPCClient) GetVoteOnHash(ctx context.Context, startBlock uint64, en
 
 func (h *BorGRPCClient) HeaderByNumber(ctx context.Context, blockID uint64) (*ethTypes.Header, error) {
 
-	blockNumberAsString := toBlockNumArg(big.NewInt(int64(blockID)))
+	if blockID > math.MaxInt64 {
+		return nil, fmt.Errorf("blockID too large: %d", blockID)
+	}
+
+	blockNumberAsString := ToBlockNumArg(big.NewInt(int64(blockID)))
 
 	req := &proto.GetHeaderByNumberRequest{
 		Number: blockNumberAsString,
@@ -83,7 +87,11 @@ func (h *BorGRPCClient) HeaderByNumber(ctx context.Context, blockID uint64) (*et
 
 func (h *BorGRPCClient) BlockByNumber(ctx context.Context, blockID uint64) (*ethTypes.Block, error) {
 
-	blockNumberAsString := toBlockNumArg(big.NewInt(int64(blockID)))
+	if blockID > math.MaxInt64 {
+		return nil, fmt.Errorf("blockID too large: %d", blockID)
+	}
+
+	blockNumberAsString := ToBlockNumArg(big.NewInt(int64(blockID)))
 
 	req := &proto.GetBlockByNumberRequest{
 		Number: blockNumberAsString,
@@ -161,12 +169,12 @@ func receiptResponseToTypesReceipt(receipt *proto.Receipt) *ethTypes.Receipt {
 	}
 }
 
-func toBlockNumArg(number *big.Int) string {
+func ToBlockNumArg(number *big.Int) string {
 	if number == nil {
 		return "latest"
 	}
 	if number.Sign() >= 0 {
-		return hexutil.EncodeBig(number)
+		return number.String()
 	}
 	// It's negative.
 	if number.IsInt64() {
```
