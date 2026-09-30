# [?] TEAL: Fix panic when checking macro names containing non-ASCII runes (#6461)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2025-10-10
Source: https://github.com/algorand/go-algorand/commit/0740b18b39e97e74ac184a523376f5c359dac244
Type: security-commit

## Details
TEAL: Fix panic when checking macro names containing non-ASCII runes (#6461)

## Patch
### data/transactions/logic/assembler.go
```diff
@@ -2207,7 +2207,7 @@ func checkMacroName(macroName string, version uint64, labels map[string]int) err
 		} else if count == 1 {
 			secondRune = r
 		}
-		if !unicode.IsLetter(r) && !unicode.IsDigit(r) && !otherAllowedChars[r] {
+		if !unicode.IsLetter(r) && !unicode.IsDigit(r) && (int(r) >= len(otherAllowedChars) || !otherAllowedChars[r]) {
 			return fmt.Errorf("%s character not allowed in macro name", string(r))
 		}
 		count++
```

### data/transactions/logic/assembler_test.go
```diff
@@ -3559,6 +3559,7 @@ add:
 		AssemblerMaxVersion,
 		exp(3, "Cannot create label with same name as macro: coolLabel"),
 	)
+	testProg(t, `#define 👩 123`, AssemblerMaxVersion, exp(1, "👩 character not allowed in macro name"))
 	// These two tests are just for coverage, they really really can't happen
 	ops := newOpStream(AssemblerMaxVersion)
 	err := define(&ops, []token{{str: "not#define"}})
```
