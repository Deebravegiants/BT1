# [?] fix(orm): int overflows on arm build (#16108)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-05-11
Source: https://github.com/cosmos/cosmos-sdk/commit/384f012f9aef3d8d2e4054058c919f46d57e8087
Type: security-commit

## Details
fix(orm): int overflows on arm build (#16108)

## Patch
### orm/encoding/ormfield/duration.go
```diff
@@ -8,10 +8,10 @@ import (
 )
 
 const (
-	DurationSecondsMin = -315576000000
-	DurationSecondsMax = 315576000000
-	DurationNanosMin   = -999999999
-	DurationNanosMax   = 999999999
+	DurationSecondsMin int64 = -315576000000
+	DurationSecondsMax int64 = 315576000000
+	DurationNanosMin         = -999999999
+	DurationNanosMax         = 999999999
 )
 
 // DurationCodec encodes google.protobuf.Duration values with the following
@@ -41,7 +41,7 @@ func (d DurationCodec) Encode(value protoreflect.Value, w io.Writer) error {
 		return fmt.Errorf("duration seconds is out of range %d, must be between %d and %d", secondsInt, DurationSecondsMin, DurationSecondsMax)
 	}
 	negative := secondsInt < 0
-	// we subtract the min duration value to make sure secondsInt is always non-negative and starts at 0
+	// we subtract the min duration value to make sure secondsInt is always non-negative and starts at 0.
 	secondsInt -= DurationSecondsMin
 	err := encodeSeconds(secondsInt, w)
 	if err != nil {
```

### orm/encoding/ormfield/timestamp.go
```diff
@@ -21,12 +21,12 @@ import (
 type TimestampCodec struct{}
 
 const (
-	timestampDurationNilValue       = 0xFF
-	timestampDurationZeroNanosValue = 0x0
-	timestampDurationBufferSize     = 9
-	TimestampSecondsMin             = -62135596800
-	TimestampSecondsMax             = 253402300799
-	TimestampNanosMax               = 999999999
+	timestampDurationNilValue             = 0xFF
+	timestampDurationZeroNanosValue       = 0x0
+	timestampDurationBufferSize           = 9
+	TimestampSecondsMin             int64 = -62135596800
+	TimestampSecondsMax             int64 = 253402300799
+	TimestampNanosMax                     = 999999999
 )
 
 var (
```
