# [H] H-08 | Protocol Loses Blast Points And WETH Rebasing Yields

## Summary
Severity: High
Contest weight: 0.3172
Dataset id: 21481
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reserve token in the protocol is Blast’s rebasing WETH token, which has automatic rebasing by default (not like the native ETH with void by default) for both EOAs and smart contracts. Normally, these reserve tokens are not held in the Baseline contracts. They are deployed into the Thruster pools, which set their WETH yield configuration as claimable in their constructor, as liquidity. So, Thruster pools earn rebasing yields from liquidity providers’ assets, and the factory owner of the pool can claim these yields. According to [Thruster docs](https://docs.thruster.finance/incentives/blast-points-and-gold#blast-points), liquidity providers earn Blast points depending on their WETH balances since they help Thruster to earn yields. Thruster says the system is automatic, but there are some checks: “Pools with a significant amount of liquidity providers being contracts (not EOAs) need to be manually verified to ensure that the Points are claimable by the contracts”. BPOOL contract itself will be the biggest liquidity provider but it has no way to claim Blast points. Therefore, the Thruster protocol [will not allocate](https://docs.thruster.finance/integration/blast-points-for-thruster-lp-integrations) these earned points to Baseline. ”…it should not be allocated to a contract address that does not support the Blast Points API as those Points then become unclaimable or transferable…”. This would also be a case if the protocol decides to deploy liquidity in another Uniswap fork.

## Recommendation
Use IERC20Rebasing interface instead of regular ERC20 for reserve token, and then configure smart contracts in a way to be integrated with Blast points system.
