# [?] fix: do not panic if registering the same error to global registry (#24568)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-05-08
Source: https://github.com/cosmos/cosmos-sdk/commit/5d28bf5540fd90530be57aaf46f53550d1a6e4a5
Type: security-commit

## Details
fix: do not panic if registering the same error to global registry (#24568)

## Patch
### errors/CHANGELOG.md
```diff
@@ -31,6 +31,10 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ## [Unreleased]
 
+### Changes
+ 
+* [#24568](https://github.com/cosmos/cosmos-sdk/pull/24568) Registering the same error code twice no longer will panic - a warning error will be logged to `stderr`.
+
 ## [v1.0.2](https://github.com/cosmos/cosmos-sdk/releases/tag/errors%2Fv1.0.2)
 
 ### Improvements 
```

### errors/README.md
```diff
@@ -0,0 +1 @@
+# Errors

This package provides structured error handling for Cosmos SDK apps. It supports:

- Custom error codes and messages
- Stack traces when wrapping errors
- ABCI-compatible responses for Tendermint
- Optional gRPC status codes

## Usage

### Registering Errors

Define root errors with a unique code and description:

```go
var ErrInvalidInput = errors.Register("app", 1001, "invalid input")
```

You can wrap errors to add context:

```go
return errors.Wrap(ErrInvalidInput, "missing field")
```

### Getting ABCI Error Info

To convert an error to ABCI-compatible output:

```go
codespace, code, log := errors.ABCIInfo(err, debug)
```

Set `debug = true` to include stack traces in logs.

### Suppress Duplicate Error Warnings

To prevent logging when the same error is registered twice, set:

```bash
export COSMOS_SDK_SUPPRESS_DUPLICATE_ERROR_CODE_LOG=true
```

Useful in tests or modules that may re-register the same error.
\ No newline at end of file
```

### errors/errors.go
```diff
@@ -2,6 +2,8 @@ package errors
 
 import (
 	"fmt"
+	"io"
+	"os"
 	"reflect"
 
 	"github.com/pkg/errors"
@@ -10,7 +12,11 @@ import (
 )
 
 // UndefinedCodespace when we explicitly declare no codespace
-const UndefinedCodespace = "undefined"
+const (
+	UndefinedCodespace = "undefined"
+	// EnvSuppressErrorDuplicateRegister can be set to 'true' to suppress any logging when errors are double-registered.
+	EnvSuppressErrorDuplicateRegister = "COSMOS_SDK_SUPPRESS_DUPLICATE_ERROR_CODE_LOG"
+)
 
 var (
 	// errInternal should never be exposed, but we reserve this code for non-specified errors
@@ -19,7 +25,7 @@ var (
 	// ErrStopIterating is used to break out of an iteration
 	ErrStopIterating = Register(UndefinedCodespace, 2, "stop iterating")
 
-	// ErrPanic should only be set when we recovering from a panic
+	// ErrPanic should only be set when recovering from a panic
 	ErrPanic = Register(UndefinedCodespace, 111222, "panic")
 )
 
@@ -38,9 +44,13 @@ func Register(codespace string, code uint32, description string) *Error {
 // RegisterWithGRPCCode is a version of Register that associates a gRPC error
 // code with a registered error.
 func RegisterWithGRPCCode(codespace string, code uint32, grpcCode grpccodes.Code, description string) *Error {
-	// TODO - uniqueness is (codespace, code) combo
 	if e := getUsed(codespace, code); e != nil {
-		panic(fmt.Sprintf("error with code %d is already registered: %q", code, e.desc))
+		if os.Getenv(EnvSuppressErrorDuplicateRegister) != "true" {
+			_, err := io.WriteString(os.Stderr, "error with code "+errorID(codespace, code)+" is already registered: "+e.desc+". Overwriting with current error...\n")
+			if err != nil {
+				panic(err)
+			}
+		}
 	}
 
 	err := &Error{codespace: codespace, code: code, desc: description, grpcCode: grpcCode}
```

### errors/errors_test.go
```diff
@@ -11,6 +11,40 @@ import (
 	grpcstatus "google.golang.org/grpc/status"
 )
 
+const testCodespace = "testtesttest"
+
+var (
+	ErrTxDecode                = Register(testCodespace, 2, "tx parse error")
+	ErrInvalidSequence         = Register(testCodespace, 3, "invalid sequence")
+	ErrUnauthorized            = Register(testCodespace, 4, "unauthorized")
+	ErrInsufficientFunds       = Register(testCodespace, 5, "insufficient funds")
+	ErrUnknownRequest          = Register(testCodespace, 6, "unknown request")
+	ErrInvalidAddress          = Register(testCodespace, 7, "invalid address")
+	ErrInvalidPubKey           = Register(testCodespace, 8, "invalid pubkey")
+	ErrUnknownAddress          = Register(testCodespace, 9, "unknown address")
+	ErrInvalidCoins            = Register(testCodespace, 10, "invalid coins")
+	ErrOutOfGas                = Register(testCodespace, 11, "out of gas")
+	ErrInsufficientFee         = Register(testCodespace, 13, "insufficient fee")
+	ErrTooManySignatures       = Register(testCodespace, 14, "maximum number of signatures exceeded")
+	ErrNoSignatures            = Register(testCodespace, 15, "no signatures supplied")
+	ErrJSONMarshal             = Register(testCodespace, 16, "failed to marshal JSON bytes")
+	ErrJSONUnmarshal           = Register(testCodespace, 17, "failed to unmarshal JSON bytes")
+	ErrInvalidRequest          = Register(testCodespace, 18, "invalid request")
+	ErrMempoolIsFull           = Register(testCodespace, 20, "mempool is full")
+	ErrTxTooLarge              = Register(testCodespace, 21, "tx too large")
+	ErrKeyNotFound             = Register(testCodespace, 22, "key not found")
+	ErrorInvalidSigner         = Register(testCodespace, 24, "tx intended signer does not match the given signer")
+	ErrInvalidChainID          = Register(testCodespace, 28, "invalid chain-id")
+	ErrInvalidType             = Register(testCodespace, 29, "invalid type")
+	ErrUnknownExtensionOptions = Register(testCodespace, 31, "unknown extension options")
+	ErrPackAny                 = Register(testCodespace, 33, "failed packing protobuf message to Any")
+	ErrLogic                   = Register(testCodespace, 35, "internal logic error")
+	ErrConflict                = RegisterWithGRPCCode(testCodespace, 36, codes.FailedPrecondition, "conflict")
+	ErrNotSupported            = RegisterWithGRPCCode(testCodespace, 37, codes.Unimplemented, "feature not supported")
+	ErrNotFound                = RegisterWithGRPCCode(testCodespace, 38, codes.NotFound, "not found")
+	ErrIO                      = Register(testCodespace, 39, "Internal IO error")
+)
+
 type errorsTestSuite struct {
 	suite.Suite
 }
@@ -19,10 +53,6 @@ func TestErrorsTestSuite(t *testing.T) {
 	suite.Run(t, new(errorsTestSuite))
 }
 
-func (s *errorsTestSuite) SetupSuite() {
-	s.T().Parallel()
-}
-
 func (s *errorsTestSuite) TestCause() {
 	std := stdlib.New("this is a stdlib error")
 
@@ -226,36 +256,18 @@ func (s *errorsTestSuite) TestGRPCStatus() {
 	s.Require().Equal("codespace testtesttest code 38: not found: test", status.Message())
 }
 
-const testCodespace = "testtesttest"
+func (s *errorsTestSuite) TestDoubleRegister() {
+	s.Require().NotPanics(func() {
+		_ = Register(testCodespace, 50, "Internal IO error")
+		_ = Register(testCodespace, 50, "Internal IO error")
+	})
+}
 
-var (
-	ErrTxDecode                = Register(testCodespace, 2, "tx parse error")
-	ErrInvalidSequence         = Register(testCodespace, 3, "invalid sequence")
-	ErrUnauthorized            = Register(testCodespace, 4, "unauthorized")
-	ErrInsufficientFunds       = Register(testCodespace, 5, "insufficient funds")
-	ErrUnknownRequest          = Register(testCodespace, 6, "unknown request")
-	ErrInvalidAddress          = Register(testCodespace, 7, "invalid address")
-	ErrInvalidPubKey           = Register(testCodespace, 8, "invalid pubkey")
-	ErrUnknownAddress          = Register(testCodespace, 9, "unknown address")
-	ErrInvalidCoins            = Register(testCodespace, 10, "invalid coins")
-	ErrOutOfGas                = Register(testCodespace, 11, "out of gas")
-	ErrInsufficientFee         = Register(testCodespace, 13, "insufficient fee")
-	ErrTooManySignatures       = Register(testCodespace, 14, "maximum number of signatures exceeded")
-	ErrNoSignatures            = Register(testCodespace, 15, "no signatures supplied")
-	ErrJSONMarshal             = Register(testCodespace, 16, "failed to marshal JSON bytes")
-	ErrJSONUnmarshal           = Register(testCodespace, 17, "failed to unmarshal JSON bytes")
-	ErrInvalidRequest          = Register(testCodespace, 18, "invalid request")
-	ErrMempoolIsFull           = Register(testCodespace, 20, "mempool is full")
-	ErrTxTooLarge              = Register(testCodespace, 21, "tx too large")
-	ErrKeyNotFound             = Register(testCodespace, 22, "key not found")
-	ErrorInvalidSigner         = Register(testCodespace, 24, "tx intended signer does not match the given signer")
-	ErrInvalidChainID          = Register(testCodespace, 28, "invalid chain-id")
-	ErrInvalidType             = Register(testCodespace, 29, "invalid type")
-	ErrUnknownExtensionOptions = Register(testCodespace, 31, "unknown extension options")
-	ErrPackAny                 = Register(testCodespace, 33, "failed packing protobuf message to Any")
-	ErrLogic                   = Register(testCodespace, 35, "internal logic error")
-	ErrConflict                = RegisterWithGRPCCode(testCodespace, 36, codes.FailedPrecondition, "conflict")
-	ErrNotSupported            = RegisterWithGRPCCode(testCodespace, 37, codes.Unimplemented, "feature not supported")
-	ErrNotFound                = RegisterWithGRPCCode(testCodespace, 38, codes.NotFound, "not found")
-	ErrIO                      = Register(testCodespace, 39, "Internal IO error")
-)
+func (s *errorsTestSuite) TestDoubleRegisterDuplicateErrorRegistration() {
+	s.T().Setenv(EnvSuppressErrorDuplicateRegister, "true")
+
+	s.Require().NotPanics(func() {
+		_ = Register(testCodespace, 50, "Internal IO error")
+		_ = Register(testCodespace, 50, "Internal IO error")
+	})
+}
```
