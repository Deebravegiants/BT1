# [?] fix: arbitrum nitro gas estimation overflows (#4947)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2024-12-05
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/4cb2c9ae416f08aff55e0abc09bfddf1f83c6513
Type: security-commit

## Details
fix: arbitrum nitro gas estimation overflows (#4947)

### Description

The originally set balance when estimating arbitrum nitro gas was
causing RPC errors, which @tkporter pointed out could be due to an
overflow in the node's code. This PR sets the balance to 100 ETH, which
does fix the error

### Drive-by changes

<!--
Are there any minor or drive-by changes also included?
-->

### Related issues

<!--
- Fixes #[issue number here]
-->

### Backward compatibility

<!--
Are these changes backward compatible? Are there any infrastructure
implications, e.g. changes that would prohibit deploying older commits
using this infra tooling?

Yes/No
-->

### Testing

<!--
What kind of testing have these changes undergone?

None/Manual/Unit Tests
-->
