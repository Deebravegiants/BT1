# [?] fix: x/tx/decode: fix (*Decoder).Decode crash with invalid length prefix (#16681)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-06-26
Source: https://github.com/cosmos/cosmos-sdk/commit/51e01819c83abc843d92fc3648f60cb1ca8945fb
Type: security-commit

## Details
fix: x/tx/decode: fix (*Decoder).Decode crash with invalid length prefix (#16681)

## Patch
### x/tx/CHANGELOG.md
```diff
@@ -31,6 +31,10 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ## [Unreleased]
 
+### Bug Fixes
+
+* [#16681](https://github.com/cosmos/cosmos-sdk/pull/16681): catch and fix `(*Decoder).Decode` crash from invalid length prefix in Tx bytes
+
 ## v0.8.0
 
 ### Improvements
```

### x/tx/decode/decode_test.go
```diff
@@ -3,6 +3,7 @@ package decode_test
 import (
 	"encoding/hex"
 	"fmt"
+	"strings"
 	"testing"
 
 	"github.com/cosmos/cosmos-proto/anyutil"
@@ -118,3 +119,31 @@ func (d dummyAddressCodec) StringToBytes(text string) ([]byte, error) {
 func (d dummyAddressCodec) BytesToString(bz []byte) (string, error) {
 	return hex.EncodeToString(bz), nil
 }
+
+func TestDecodeTxBodyPanic(t *testing.T) {
+	crashVector := []byte{
+		0x0a, 0x0a, 0x09, 0xe7, 0xbf, 0xba, 0xe6, 0x82, 0x9a, 0xe6, 0xaa, 0x30,
+	}
+
+	cdc := new(dummyAddressCodec)
+	signingCtx, err := signing.NewContext(signing.Options{
+		AddressCodec:          cdc,
+		ValidatorAddressCodec: cdc,
+	})
+	if err != nil {
+		t.Fatal(err)
+	}
+	dec, err := decode.NewDecoder(decode.Options{
+		SigningContext: signingCtx,
+	})
+	if err != nil {
+		t.Fatal(err)
+	}
+	_, err = dec.Decode(crashVector)
+	if err == nil {
+		t.Fatal("expected a non-nil error")
+	}
+	if g, w := err.Error(), "could not consume length prefix"; !strings.Contains(g, w) {
+		t.Fatalf("error mismatch\n%s\ndoes not contain\n\t%q", g, w)
+	}
+}
```

### x/tx/decode/unknown.go
```diff
@@ -85,6 +85,15 @@ func RejectUnknownFields(bz []byte, desc protoreflect.MessageDescriptor, allowUn
 
 		// consume length prefix of nested message
 		_, o := protowire.ConsumeVarint(fieldBytes)
+		if o < 0 {
+			err = fmt.Errorf("could not consume length prefix fieldBytes for nested message: %v: %w",
+				fieldMessage, protowire.ParseError(o))
+			return hasUnknownNonCriticals, err
+		} else if o > len(fieldBytes) {
+			err = fmt.Errorf("length prefix > len(fieldBytes) for nested message: %v", fieldMessage)
+			return hasUnknownNonCriticals, err
+		}
+
 		fieldBytes = fieldBytes[o:]
 
 		var err error
```
