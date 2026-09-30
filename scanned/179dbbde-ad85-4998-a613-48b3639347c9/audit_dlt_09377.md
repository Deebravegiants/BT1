# [?] fix(types): avoid panic on unmarshalling of empty inputs (#2511)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2025-02-14
Source: https://github.com/berachain/beacon-kit/commit/50e8eec63e7af2445363ee56edec45cbbc141741
Type: security-commit

## Details
fix(types): avoid panic on unmarshalling of empty inputs (#2511)

Co-authored-by: Cal Bera <calbera@berachain.com>

## Patch
### primitives/common/consensus.go
```diff
@@ -23,6 +23,7 @@ package common
 import (
 	stdbytes "bytes"
 
+	"github.com/berachain/beacon-kit/errors"
 	"github.com/berachain/beacon-kit/primitives/bytes"
 	"github.com/berachain/beacon-kit/primitives/encoding/hex"
 	"github.com/berachain/beacon-kit/primitives/encoding/json"
@@ -64,6 +65,10 @@ type Root [RootSize]byte
 const RootSize = 32
 
 // NewRootFromHex creates a new root from a hex string.
+//
+// Errors if:
+// - input is not prefixed with "0x".
+// - input is not valid hex of 32 bytes.
 func NewRootFromHex(input string) (Root, error) {
 	val, err := hex.ToBytes(input)
 	if err != nil {
@@ -114,6 +119,15 @@ func (r Root) MarshalJSON() ([]byte, error) {
 }
 
 // UnmarshalJSON parses a root in hex syntax.
+//
+// NOTE: Enforces the input to include any extra character in the first and last position.
+// Technically this is used to remove the quote `"`. For example, the input may look like:
+// []byte(`"0x6969696969696969696969696969696969696969696969696969696969696969"`)
 func (r *Root) UnmarshalJSON(input []byte) error {
+	if len(input) <= 1 {
+		return errors.Wrapf(
+			bytes.ErrIncorrectLength, "input length (%d) is too small", len(input),
+		)
+	}
 	return r.UnmarshalText(input[1 : len(input)-1])
 }
```

### primitives/common/consensus_test.go
```diff
@@ -84,3 +84,59 @@ func TestNewRootFromHex(t *testing.T) {
 		})
 	}
 }
+
+func TestRoot_UnmarshalJSON(t *testing.T) {
+	t.Parallel()
+	tests := []struct {
+		name        string
+		input       []byte
+		expectedErr error
+	}{
+		{
+			name:        "nil input",
+			input:       nil,
+			expectedErr: bytes.ErrIncorrectLength,
+		},
+		{
+			name:        "empty input",
+			input:       []byte(``),
+			expectedErr: bytes.ErrIncorrectLength,
+		},
+		{
+			name:        "short input of 1 byte",
+			input:       []byte{0x01},
+			expectedErr: bytes.ErrIncorrectLength,
+		},
+		{
+			name:        "short input of just quotes",
+			input:       []byte(`""`),
+			expectedErr: hex.ErrEmptyString,
+		},
+		{
+			name:        "valid input",
+			input:       []byte(`"0x6969696969696969696969696969696969696969696969696969696969696969"`),
+			expectedErr: nil,
+		},
+	}
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			t.Parallel()
+			var (
+				r     common.Root
+				err   error
+				input = tt.input
+			)
+
+			f := func() {
+				err = r.UnmarshalJSON(input)
+			}
+			require.NotPanics(t, f)
+
+			if tt.expectedErr != nil {
+				require.ErrorContains(t, err, tt.expectedErr.Error())
+			} else {
+				require.NoError(t, err)
+			}
+		})
+	}
+}
```

### primitives/common/execution.go
```diff
@@ -21,9 +21,11 @@
 package common
 
 import (
-	"bytes"
+	stdbytes "bytes"
 	"encoding"
 
+	"github.com/berachain/beacon-kit/errors"
+	"github.com/berachain/beacon-kit/primitives/bytes"
 	"github.com/berachain/beacon-kit/primitives/encoding/hex"
 	"github.com/berachain/beacon-kit/primitives/encoding/json"
 	"golang.org/x/crypto/sha3"
@@ -70,6 +72,10 @@ func (h ExecutionHash) MarshalText() ([]byte, error) {
 }
 
 // UnmarshalText parses a hash in hex syntax.
+//
+// Errors if:
+// - input is not "0x" prefixed.
+// - input length is not 66.
 func (h *ExecutionHash) UnmarshalText(input []byte) error {
 	return hex.DecodeFixedText(input, h[:])
 }
@@ -80,6 +86,10 @@ func (h ExecutionHash) MarshalJSON() ([]byte, error) {
 }
 
 // UnmarshalJSON parses a hash in hex syntax.
+//
+// NOTE: Enforces the input to include the `"` characters in first and last position.
+// For example, the input may look like:
+// []byte(`"0x6969696969696969696969696969696969696969696969696969696969696969"`)
 func (h *ExecutionHash) UnmarshalJSON(input []byte) error {
 	return hex.DecodeFixedJSON(input, h[:])
 }
@@ -100,7 +110,7 @@ func NewExecutionAddressFromHex(input string) ExecutionAddress {
 
 // Equals returns true if the two addresses are the same.
 func (a ExecutionAddress) Equals(other ExecutionAddress) bool {
-	return bytes.Equal(a[:], other[:])
+	return stdbytes.Equal(a[:], other[:])
 }
 
 // Hex converts an address to a hex string.
@@ -118,6 +128,10 @@ func (a ExecutionAddress) MarshalText() ([]byte, error) {
 }
 
 // UnmarshalText parses an address in hex syntax.
+//
+// Errors if:
+// - input is not "0x" prefixed.
+// - input length is not 42.
 func (a *ExecutionAddress) UnmarshalText(input []byte) error {
 	return hex.DecodeFixedText(input, a[:])
 }
@@ -128,7 +142,16 @@ func (a ExecutionAddress) MarshalJSON() ([]byte, error) {
 }
 
 // UnmarshalJSON parses an address in hex syntax.
+//
+// NOTE: Enforces the input to include any extra character in the first and last position.
+// Technically this is used to remove the quote `"`. For example, the input may look like:
+// []byte(`"0x6969696969696969696969696969696969696969"`)
 func (a *ExecutionAddress) UnmarshalJSON(input []byte) error {
+	if len(input) <= 1 {
+		return errors.Wrapf(
+			bytes.ErrIncorrectLength, "input length (%d) is too small", len(input),
+		)
+	}
 	return a.UnmarshalText(input[1 : len(input)-1])
 }
 
```

### primitives/common/execution_test.go
```diff
@@ -24,6 +24,7 @@ import (
 	"encoding/json"
 	"testing"
 
+	"github.com/berachain/beacon-kit/primitives/bytes"
 	"github.com/berachain/beacon-kit/primitives/common"
 	"github.com/berachain/beacon-kit/primitives/encoding/hex"
 	"github.com/stretchr/testify/require"
@@ -69,3 +70,59 @@ func TestExecutionAddressMarshalling(t *testing.T) {
 		})
 	}
 }
+
+func TestExecutionAddressUnmarshalJSON_Short(t *testing.T) {
+	t.Parallel()
+	tests := []struct {
+		name        string
+		input       []byte
+		expectedErr error
+	}{
+		{
+			name:        "empty input",
+			input:       []byte(``),
+			expectedErr: bytes.ErrIncorrectLength,
+		},
+		{
+			name:        "nil input",
+			input:       nil,
+			expectedErr: bytes.ErrIncorrectLength,
+		},
+		{
+			name:        "short input of 1 byte",
+			input:       []byte{0x01},
+			expectedErr: bytes.ErrIncorrectLength,
+		},
+		{
+			name:        "short input of just quotes",
+			input:       []byte(`""`),
+			expectedErr: hex.ErrInvalidHexStringLength,
+		},
+		{
+			name:        "valid input",
+			input:       []byte(`"0x6969696969696969696969696969696969696969"`),
+			expectedErr: nil,
+		},
+	}
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			t.Parallel()
+			var (
+				addr  common.ExecutionAddress
+				err   error
+				input = tt.input
+			)
+
+			f := func() {
+				err = addr.UnmarshalJSON(input)
+			}
+			require.NotPanics(t, f)
+
+			if tt.expectedErr != nil {
+				require.ErrorContains(t, err, tt.expectedErr.Error())
+			} else {
+				require.NoError(t, err)
+			}
+		})
+	}
+}
```
