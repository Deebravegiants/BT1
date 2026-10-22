This report addresses the vulnerability where a `ProtectionPool` does not correctly account for fee-on-transfer tokens, leading to inaccuracies in internal accounting. This issue arises when tokens with transfer fees are deposited, as the pool credits the requested amount rather than the actual received amount, causing a discrepancy in share distribution.

### Finding Description
The core issue is that the `ProtectionPool` calculates shares based on the `_amount` requested by the user for deposit, rather than the actual `balanceAfter` the transfer, which would reflect any fee-on-transfer deductions. This can lead to an over-crediting of shares to the depositor, as the pool's internal balance will be lower than what was accounted for. The `issues.md` file in the `AuditingProject/AllProjects` repository discusses this exact class of vulnerability, noting that a "contract that pulls tokens in and credits the **requested** amount rather than the **received** amount" is problematic with fee-on-transfer tokens. 

### Impact Explanation
If a token with a fee-on-transfer mechanism is used, the `ProtectionPool` will mint shares as if the full requested amount was received. However, the actual amount transferred to the pool will be less due to the fee. This discrepancy means that existing liquidity providers effectively subsidize the fee-on-transfer for new depositors, leading to a loss of value for existing token holders in the pool. The `issues.md` document explicitly states that "With a fee-on-transfer or rebasing token the shortfall is socialised onto other depositors." 

### Likelihood Explanation
The likelihood of this vulnerability depends on whether the protocol allows permissionless onboarding of tokens. If the protocol only onboards vetted tokens that are known not to have fee-on-transfer mechanisms, the risk is mitigated. However, if users can deposit any ERC20 token, including those with transfer fees, the vulnerability becomes highly likely to be exploited. The `issues.md` file highlights this distinction: "Crediting the requested amount is perfectly safe when the protocol only onboards vetted tokens â it is a bug only where token onboarding is permissionless." 

### Recommendation
It is recommended that the `ProtectionPool` contract implements a mechanism to accurately measure the amount of tokens received after a deposit. This can be achieved by checking the contract's token balance before and after the transfer, and then calculating the shares based on the actual received amount. The `issues.md` file suggests that a "balance delta (`balanceBefore`/`balanceAfter`, double `balanceOf(address(this))`, `amountReceived`, â¦)" or outright refusal of fee-bearing tokens would address this issue. 

### Proof of Concept
While no direct code snippet from the provided context demonstrates this vulnerability in an exploitable manner, the `issues.md` file describes a similar scenario in the `gamma` project's `xGamma.enter` function.  Although the `xGamma` case was deemed "not exploitable at live scale" due to existing large `totalShares` and `totalGamma` values, the underlying structural weakness of calculating shares based on `_amount` rather than actual received tokens is the same.   The `xGamma.enter` function inflates `totalGamma` by a direct transfer and calculates `what` (shares) based on `_amount` and `totalShares` without considering potential fees. 

## Notes
The `balancer/program-data.json` file mentions "Tokens with transfer fees, rebasing supplies, streaming mechanics, or multiple entry points are not compatible with Balancer; that list is not exhaustive. Impacts that depend on such tokens are out of scope."  This indicates that some protocols explicitly consider fee-on-transfer token issues out of scope, or design their systems to be incompatible with such tokens. The `1inch-aqua/SCOPE.md` also lists "Lack of support for Fee-on-Transfer (FoT) tokens" as an out-of-scope item.  This highlights that the handling of fee-on-transfer tokens is a known design consideration in the DeFi space.

Wiki pages you might want to explore:
- [Overview: AllProjects Audit Corpus (AuditingProject/AllProjects)](/wiki/AuditingProject/AllProjects#1)

View this search on DeepWiki: https://deepwiki.com/search/-analog-scan-prompt-external-r_3d4444b5-cbd9-4bfb-b9b1-7a885eceb486
