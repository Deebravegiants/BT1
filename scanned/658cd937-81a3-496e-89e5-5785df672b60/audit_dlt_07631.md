# [?] tests/fuzzers/abi: fixed one-off panic with int.Min64 value (#22233)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-01-25
Source: https://github.com/ethereum/go-ethereum/commit/7202b410b064c17c0648c4c6c212dc4c2a787907
Type: security-commit

## Details
tests/fuzzers/abi: fixed one-off panic with int.Min64 value (#22233)

* tests/fuzzers/abi: fixed one-off panic with int.Min64 value

* tests/fuzzers/abi: fixed one-off panic with int.Min64 value

## Patch
### tests/fuzzers/abi/abifuzzer.go
```diff
@@ -161,7 +161,10 @@ func getUInt(fuzzer *fuzz.Fuzzer) int {
 	var i int
 	fuzzer.Fuzz(&i)
 	if i < 0 {
-		i *= -1
+		i = -i
+		if i < 0 {
+			return 0
+		}
 	}
 	return i
 }
```

### tests/fuzzers/abi/abifuzzer_test.go
```diff
@@ -23,9 +23,7 @@ import (
 // TestReplicate can be used to replicate crashers from the fuzzing tests.
 // Just replace testString with the data in .quoted
 func TestReplicate(t *testing.T) {
-	testString := "N\xef\xbf0\xef\xbf99000000000000" +
-		"000000000000"
-
+	testString := "\x20\x20\x20\x20\x20\x20\x20\x20\x80\x00\x00\x00\x20\x20\x20\x20\x00"
 	data := []byte(testString)
 	runFuzzer(data)
 }
```
