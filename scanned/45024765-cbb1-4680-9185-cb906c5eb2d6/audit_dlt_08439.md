# [?] fix non-deterministic spend limit test (#8120)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2024-04-22
Source: https://github.com/osmosis-labs/osmosis/commit/5b5ab3f7202f430ced2f47a45893439afb295091
Type: security-commit

## Details
fix non-deterministic spend limit test (#8120)

## Patch
### x/smart-account/authenticator/spend_limits_test.go
```diff
@@ -281,7 +281,7 @@ func (s *SpendLimitAuthenticatorTest) TestSpendLimit() {
 	s.Require().Contains(
 		err.Error(),
 		fmt.Sprintf(
-			"Current time %d.%d not within time limit None - %s.%s: execute wasm contract failed",
+			"Current time %d.%09d not within time limit None - %s.%s: execute wasm contract failed",
 			s.Ctx.BlockTime().Unix(), s.Ctx.BlockTime().Nanosecond(),
 			endTimeSecsStr, endTimeNanosStr,
 		),
```
