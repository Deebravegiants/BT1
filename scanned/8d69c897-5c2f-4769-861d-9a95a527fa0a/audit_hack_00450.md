# [M] Aurellion Labs incident: Aurellion Labs' Diamond Proxy contract (EIP-2535) was exploited due to an unprotected initialize(address) function in the SafeOwna

## Summary
Severity: Medium
Target: Aurellion Labs
Loss: $ 456,000
Attack method: Smart Contract Vulnerability
Published: 2026-05-12
Source: https://x.com/SlowMist_Team/status/2054163700035289446
Type: slowmist-incident

## Details
Aurellion Labs' Diamond Proxy contract (EIP-2535) was exploited due to an unprotected initialize(address) function in the SafeOwnable Facet. Although an owner was set, the OpenZeppelin-style _initialized storage slot remained 0, allowing re-initialization. The attacker called initialize() to take ownership, used diamondCut to add a malicious facet with pullERC20/sweep functions, and drained USDC from wallets that had previously approved the diamond proxy. The project paused operations, committed to reimbursing users, and advised revoking old approvals.
