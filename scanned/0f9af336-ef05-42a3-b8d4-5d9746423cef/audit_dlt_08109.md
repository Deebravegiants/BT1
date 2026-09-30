# [?] fuzz: avoid buffer overflow in bech32 target

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-03-15
Source: https://github.com/ElementsProject/lightning/commit/07527d9fbbecdc5bce1f3501cdd8037fa9246e0a
Type: security-commit

## Details
fuzz: avoid buffer overflow in bech32 target

If the fuzzer passes an empty data buffer, the fuzz target currently
attempts to read from it. We should short-circuit instead.

## Patch
### tests/fuzz/fuzz-bech32.c
```diff
@@ -19,6 +19,9 @@ void run(const uint8_t *data, size_t size)
 	int wit_version;
 	bech32_encoding benc;
 
+	if (size < 1)
+		return;
+
 	/* Buffer size is defined in each function's doc comment. */
 	bech32_str = malloc(size + strlen(hrp_inv) + 8);
 	benc = data[0] ? BECH32_ENCODING_BECH32 : BECH32_ENCODING_BECH32M;
```
