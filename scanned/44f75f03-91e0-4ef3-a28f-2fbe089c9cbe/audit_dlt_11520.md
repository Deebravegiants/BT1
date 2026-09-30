# [?] fix: remove panic from default case in signature_set.go (#6830)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-03-13
Source: https://github.com/celestiaorg/celestia-app/commit/98adca69d1781eaa84ef2a5305f13cfdec42a6eb
Type: security-commit

## Details
fix: remove panic from default case in signature_set.go (#6830)

## Summary
- Removes `panic("unreachable")` from `NotEnoughSignaturesError.Error()`
in `fibre/validator/signature_set.go`
- Replaces the `switch` statement with a direct return of the formatted
error string
- A panic in production would crash the Fibre server; the switch was
unnecessary since the error message is valid regardless of field values

Closes #6713

## Test plan
- [x] Existing tests pass: `go test ./fibre/validator/...`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/celestiaorg/celestia-app/pull/6830"
target="_blank">
  <picture>
<source media="(prefers-color-scheme: dark)"
srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
<img
src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1"
alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### fibre/validator/signature_set.go
```diff
@@ -94,10 +94,5 @@ type NotEnoughSignaturesError struct {
 }
 
 func (e *NotEnoughSignaturesError) Error() string {
-	switch {
-	case e.CollectedPower < e.RequiredPower:
-		return fmt.Sprintf("not enough voting power: collected %d, required %d", e.CollectedPower, e.RequiredPower)
-	default:
-		panic("unreachable")
-	}
+	return fmt.Sprintf("not enough voting power: collected %d, required %d", e.CollectedPower, e.RequiredPower)
 }
```
