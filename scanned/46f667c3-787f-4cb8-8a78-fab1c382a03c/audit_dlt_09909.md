# [?] Merge pull request #978 from 2dvorak/fix/rpc-tx-json-empty-signatures-panic

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-09-21
Source: https://github.com/kaiachain/kaia/commit/3a136e9ecbb7b6584752c46fcfe1c0cce34eef21
Type: security-commit

## Details
Merge pull request #978 from 2dvorak/fix/rpc-tx-json-empty-signatures-panic

blockchain/types: guard tx JSON decoders against empty signatures

## Patch
### api/api_kaia_transaction_test.go
```diff
@@ -2,6 +2,7 @@ package api
 
 import (
 	"context"
+	"encoding/json"
 	"math/big"
 	"reflect"
 	"testing"
@@ -64,6 +65,34 @@ var (
 	feePayerPrvKey, _ = crypto.HexToECDSA("aebb680a5e596c1d1a01bac78a3985b62c685c5e995d780c176138cb2679ba3e")
 )
 
+func TestSendTxArgsUnmarshalSignatures(t *testing.T) {
+	testcases := []struct {
+		name    string
+		input   string
+		wantErr bool
+	}{
+		{"missing", `{}`, false},
+		{"null", `{"signatures":null}`, false},
+		{"empty", `{"signatures":[]}`, false},
+		{"null_element", `{"signatures":[null]}`, true},
+		{"empty_element", `{"signatures":[{}]}`, true},
+		{"partial_element", `{"signatures":[{"V":"0x1"}]}`, true},
+	}
+
+	for _, tc := range testcases {
+		t.Run(tc.name, func(t *testing.T) {
+			var args SendTxArgs
+			err := json.Unmarshal([]byte(tc.input), &args)
+			if tc.wantErr {
+				assert.Error(t, err)
+			} else {
+				assert.NoError(t, err)
+				assert.Empty(t, args.TxSignatures)
+			}
+		})
+	}
+}
+
 // TestTxTypeSupport tests tx type support of APIs in KaiaTransactionAPI.
 func TestTxTypeSupport(t *testing.T) {
 	var ctx context.Context
```

### blockchain/types/tx_internal_data.go
```diff
@@ -110,6 +110,8 @@ var (
 	errUndefinedTxType                        = errors.New("undefined tx type")
 	errCannotBeSignedByFeeDelegator           = errors.New("this transaction type cannot be signed by a fee delegator")
 	errUndefinedKeyRemains                    = errors.New("undefined key remains")
+	errEmptyTxSignatures                      = errors.New("tx signatures must not be empty")
+	errInvalidTxSignatureJSON                 = errors.New("invalid tx signature JSON")
 
 	errValueKeyHumanReadableMustBool     = errors.New("HumanReadable must be a type of bool")
 	errValueKeyAccountKeyMustAccountKey  = errors.New("AccountKey must be a type of AccountKey")
```

### blockchain/types/tx_internal_data_ethereum_access_list.go
```diff
@@ -391,6 +391,9 @@ func (t *TxInternalDataEthereumAccessList) UnmarshalJSON(bytes []byte) error {
 	t.Amount = (*big.Int)(js.Amount)
 	t.Payload = js.Payload
 	t.AccessList = js.AccessList
+	if len(js.TxSignatures) == 0 || js.TxSignatures[0] == nil {
+		return errEmptyTxSignatures
+	}
 	t.V = (*big.Int)(js.TxSignatures[0].V)
 	t.R = (*big.Int)(js.TxSignatures[0].R)
 	t.S = (*big.Int)(js.TxSignatures[0].S)
```

### blockchain/types/tx_internal_data_ethereum_blob.go
```diff
@@ -738,6 +738,9 @@ func (t *TxInternalDataEthereumBlob) UnmarshalJSON(bytes []byte) error {
 	t.AccessList = js.AccessList
 	t.BlobFeeCap = (*uint256.Int)(js.BlobFeeCap)
 	t.BlobHashes = js.BlobHashes
+	if len(js.TxSignatures) == 0 || js.TxSignatures[0] == nil {
+		return errEmptyTxSignatures
+	}
 	t.V = (*big.Int)(js.TxSignatures[0].V)
 	t.R = (*big.Int)(js.TxSignatures[0].R)
 	t.S = (*big.Int)(js.TxSignatures[0].S)
```

### blockchain/types/tx_internal_data_ethereum_dynamic_fee.go
```diff
@@ -396,6 +396,9 @@ func (t *TxInternalDataEthereumDynamicFee) UnmarshalJSON(bytes []byte) error {
 	t.Amount = (*big.Int)(js.Amount)
 	t.Payload = js.Payload
 	t.AccessList = js.AccessList
+	if len(js.TxSignatures) == 0 || js.TxSignatures[0] == nil {
+		return errEmptyTxSignatures
+	}
 	t.V = (*big.Int)(js.TxSignatures[0].V)
 	t.R = (*big.Int)(js.TxSignatures[0].R)
 	t.S = (*big.Int)(js.TxSignatures[0].S)
```

### blockchain/types/tx_internal_data_ethereum_set_code.go
```diff
@@ -430,6 +430,9 @@ func (t *TxInternalDataEthereumSetCode) UnmarshalJSON(bytes []byte) error {
 	t.Payload = js.Payload
 	t.AccessList = js.AccessList
 	t.AuthorizationList = js.AuthorizationList
+	if len(js.TxSignatures) == 0 || js.TxSignatures[0] == nil {
+		return errEmptyTxSignatures
+	}
 	t.V = (*big.Int)(js.TxSignatures[0].V)
 	t.R = (*big.Int)(js.TxSignatures[0].R)
 	t.S = (*big.Int)(js.TxSignatures[0].S)
```

### blockchain/types/tx_internal_data_json_signatures_test.go
```diff
@@ -0,0 +1,111 @@
+// Copyright 2026 The Kaia Authors
+// This file is part of the kaia library.
+//
+// The kaia library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The kaia library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the kaia library. If not, see <http://www.gnu.org/licenses/>.
+
+package types
+
+import (
+	"encoding/json"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+)
+
+func TestTxInternalDataUnmarshalJSONEmptySignatures(t *testing.T) {
+	types := []struct {
+		name string
+		gen  func() TxInternalData
+	}{
+		{"Legacy", genLegacyTransaction},
+		{"EthereumAccessList", genAccessListTransaction},
+		{"EthereumDynamicFee", genDynamicFeeTransaction},
+		{"EthereumSetCode", genSetCodeTransaction},
+		{"EthereumBlob", genBlobTransaction},
+		{"ValueTransfer", genValueTransferTransaction},
+		{"FeeDelegatedValueTransfer", genFeeDelegatedValueTransferTransaction},
+	}
+
+	testcases := map[string]struct {
+		value       interface{}
+		expectedErr error
+	}{
+		"empty":           {[]interface{}{}, errEmptyTxSignatures},
+		"null_element":    {[]interface{}{nil}, errInvalidTxSignatureJSON},
+		"empty_element":   {[]interface{}{map[string]interface{}{}}, errInvalidTxSignatureJSON},
+		"partial_element": {[]interface{}{map[string]interface{}{"V": "0x1"}}, errInvalidTxSignatureJSON},
+		"missing":         {nil, errEmptyTxSignatures},
+	}
+
+	for _, tt := range types {
+		for sigName, tc := range testcases {
+			t.Run(tt.name+"/"+sigName, func(t *testing.T) {
+				raw, err := json.Marshal(tt.gen())
+				require.NoError(t, err)
+
+				var m map[string]interface{}
+				require.NoError(t, json.Unmarshal(raw, &m))
+				if sigName == "missing" {
+					delete(m, "signatures")
+				} else {
+					m["signatures"] = tc.value
+				}
+				tampered, err := json.Marshal(m)
+				require.NoError(t, err)
+
+				dec := newTxInternalDataSerializer()
+				require.NotPanics(t, func() {
+					err = json.Unmarshal(tampered, dec)
+				})
+				require.ErrorIs(t, err, tc.expectedErr)
+			})
+		}
+	}
+}
+
+func TestTxInternalDataUnmarshalJSONEmptyFeePayerSignatures(t *testing.T) {
+	testcases := map[string]struct {
+		value       interface{}
+		expectedErr error
+	}{
+		"empty":           {[]interface{}{}, errEmptyTxSignatures},
+		"null_element":    {[]interface{}{nil}, errInvalidTxSignatureJSON},
+		"empty_element":   {[]interface{}{map[string]interface{}{}}, errInvalidTxSignatureJSON},
+		"partial_element": {[]interface{}{map[string]interface{}{"V": "0x1"}}, errInvalidTxSignatureJSON},
+		"missing":         {nil, errEmptyTxSignatures},
+	}
+
+	for sigName, tc := range testcases {
+		t.Run(sigName, func(t *testing.T) {
+			raw, err := json.Marshal(genFeeDelegatedValueTransferTransaction())
+			require.NoError(t, err)
+
+			var m map[string]interface{}
+			require.NoError(t, json.Unmarshal(raw, &m))
+			if sigName == "missing" {
+				delete(m, "feePayerSignatures")
+			} else {
+				m["feePayerSignatures"] = tc.value
+			}
+			tampered, err := json.Marshal(m)
+			require.NoError(t, err)
+
+			dec := newTxInternalDataSerializer()
+			require.NotPanics(t, func() {
+				err = json.Unmarshal(tampered, dec)
+			})
+			require.ErrorIs(t, err, tc.expectedErr)
+		})
+	}
+}
```

### blockchain/types/tx_internal_data_legacy.go
```diff
@@ -291,6 +291,9 @@ func (t *TxInternalDataLegacy) UnmarshalJSON(b []byte) error {
 	t.Recipient = js.Recipient
 	t.Amount = (*big.Int)(js.Amount)
 	t.Payload = js.Payload
+	if len(js.TxSignatures) == 0 || js.TxSignatures[0] == nil {
+		return errEmptyTxSignatures
+	}
 	t.V = (*big.Int)(js.TxSignatures[0].V)
 	t.R = (*big.Int)(js.TxSignatures[0].R)
 	t.S = (*big.Int)(js.TxSignatures[0].S)
```

### blockchain/types/tx_internal_data_serializer.go
```diff
@@ -33,7 +33,9 @@ type TxInternalDataSerializer struct {
 
 // txInternalDataJSON is an internal object for JSON serialization.
 type txInternalDataJSON struct {
-	TxType TxType `json:"typeInt"`
+	TxType             TxType           `json:"typeInt"`
+	TxSignatures       TxSignaturesJSON `json:"signatures"`
+	FeePayerSignatures TxSignaturesJSON `json:"feePayerSignatures"`
 }
 
 // newTxInternalDataSerializerWithValues creates a new TxInternalDataSerializer object with the given TxInternalData object.
@@ -110,6 +112,12 @@ func (serializer *TxInternalDataSerializer) UnmarshalJSON(b []byte) error {
 	if err := json.Unmarshal(b, &dec); err != nil {
 		return err
 	}
+	if len(dec.TxSignatures) == 0 {
+		return errEmptyTxSignatures
+	}
+	if dec.TxType.IsFeeDelegatedTransaction() && len(dec.FeePayerSignatures) == 0 {
+		return errEmptyTxSignatures
+	}
 
 	if dec.TxType == TxTypeLegacyTransaction {
 		// fallback to unmarshal the legacy transaction.
```

### blockchain/types/tx_signatures.go
```diff
@@ -164,6 +164,20 @@ func (t TxSignatures) ToJSON() TxSignaturesJSON {
 // TxSignaturesJSON is an array of *TxSignatureJSON. This structure is for JSON marshalling.
 type TxSignaturesJSON []*TxSignatureJSON
 
+func (t *TxSignaturesJSON) UnmarshalJSON(b []byte) error {
+	var sigs []*TxSignatureJSON
+	if err := json.Unmarshal(b, &sigs); err != nil {
+		return err
+	}
+	for _, sig := range sigs {
+		if sig == nil || sig.V == nil || sig.R == nil || sig.S == nil {
+			return errInvalidTxSignatureJSON
+		}
+	}
+	*t = sigs
+	return nil
+}
+
 func (t TxSignaturesJSON) ToTxSignatures() TxSignatures {
 	sigs := make(TxSignatures, len(t))
 
```
