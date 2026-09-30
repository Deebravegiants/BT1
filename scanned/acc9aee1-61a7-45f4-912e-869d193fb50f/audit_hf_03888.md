# [M] Vault._amount_per_base_lp_share should also

## Summary
Severity: Medium
Contest weight: 0.2397
Dataset id: 20172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unstoppable's vault consists of two types of pools. The safety module pool is designed to bear the first loss risk. So the bad debt is first covered by the safety. Liquidity Providers have the choice to provide liquidity in the "Base LP" pool or the "Safety Module" pool. The Safety Module pool takes a first loss risk protecting the Base LP in exchange for a higher share of the trading and accruing interest. However, if the safety module liquidity is insufficient, the base liquidity is also used to cover the bad debt. But Vault._amount_per_base_lp_share never take bad debt into consideration, leading to loss of funds. When calling Vault.withdraw_liquidity, it uses Vault._account_for_withdraw_liquidity to calculate the withdraw share. If the base pool is chosen, it calls self._amount_per_base_lp_share. And it directly uses self.base_lp_total_amount to calculate the shares without considering the. Suppose that base_lp_total_amount is 100 and safety_module_lp_total_amount is 100. The bad_debt is now 150 and total_debt_amount is 0. The available liquidity is. Consider the following situations. • The total share of base liquidity is 100 shares, with Alice and Bob each having 50 shares. • Alice calls withdraw_liquidity to withdraw 50 tokens from the base pool. • Bob also wants to withdraw the liquidity but he fails since the available. If the amount of bad debt is more than safe module liquidity, the withdrawal of base liquidity becomes unfair. Early liquidity providers have the advantage of being able to withdraw the full amount, while other liquidity providers are unable to withdraw any liquidity, resulting in a loss of funds for them.

## Recommendation
If the bad debt exceeds the available safety module liquidity, _amount_per_base_lp_share should take bad debt into consideration.
def _amount_per_base_lp_share(_token: address) -> uint256:
    return (
        self._base_total_amount(_token)
        * PRECISION
    ) / self.base_lp_total_shares[_token]

@internal
@view
def _base_total_amount(_token: address) -> uint256:
    if self.bad_debt[_token] > self.safety_module_lp_total_amount[_token] + self.base_lp_total_amount[_token]:
        return 0
    if self.bad_debt[_token] <= self.safety_module_lp_total_amount[_token]:
        return self.base_lp_total_amount[_token]
    return self.safety_module_lp_total_amount[_token] + self.base_lp_total_amount[_token] - self.bad_debt[_token]
