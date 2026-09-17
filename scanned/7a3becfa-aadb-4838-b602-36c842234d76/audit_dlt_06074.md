# [?] fix: Panic instead of logging error of failing header validation (#2231)

## Summary
Severity: Unknown
Chain: Rollkit
Component: rollkit/rollkit
Published: 2025-05-13
Source: https://github.com/evstack/ev-node/commit/8765196fe32fb96a6c161825e9dbade6af51bf1d
Type: security-commit

## Details
fix: Panic instead of logging error of failing header validation (#2231)

<!--
Please read and fill out this form before submitting your PR.

Please make sure you have reviewed our contributors guide before
submitting your
first PR.

NOTE: PR titles should follow semantic commits:
https://www.conventionalcommits.org/en/v1.0.0/
-->

## Overview
Closes: #2182 

<!-- 
Please provide an explanation of the PR, including the appropriate
context,
background, goal, and rationale. If there is an issue with this
information,
please provide a tl;dr and link the issue. 

Ex: Closes #<issue number>
-->


<!-- This is an auto-generated comment: release notes by coderabbit.ai
-->
## Summary by CodeRabbit

- **Bug Fixes**
- Improved error handling during block publishing to ensure immediate
termination if block header validation fails, enhancing system
reliability.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

---------

Co-authored-by: Alexander Peters <alpe@users.noreply.github.com>

### block/manager.go
```diff
@@ -559,15 +559,6 @@ func (m *Manager) publishBlockInternal(ctx context.Context) error {
 		}
 	}
 
-	newState, err := m.applyBlock(ctx, header, data)
-	if err != nil {
-		if ctx.Err() != nil {
-			return err
-		}
-		// if call to applyBlock fails, we halt the node, see https://github.com/cometbft/cometbft/pull/496
-		panic(err)
-	}
-
 	signature, err = m.getSignature(header.Header)
 	if err != nil {
 		return err
@@ -577,8 +568,17 @@ func (m *Manager) publishBlockInternal(ctx context.Context) error {
 	header.Signature = signature
 
 	if err := header.ValidateBasic(); err != nil {
-		// TODO(tzdybal): I think this is could be even a panic, because if this happens, header is FUBAR
-		m.logger.Error("header validation error", "error", err)
+		// If this ever happens, for recovery, check for a mismatch between the configured signing key and the proposer address in the genesis file
+		panic(fmt.Errorf("critical: newly produced header failed validation: %w", err))
+	}
+
+	newState, err := m.applyBlock(ctx, header, data)
+	if err != nil {
+		if ctx.Err() != nil {
+			return err
+		}
+		// if call to applyBlock fails, we halt the node, see https://github.com/cometbft/cometbft/pull/496
+		panic(err)
 	}
 
 	// append metadata to Data before validating and saving
```
