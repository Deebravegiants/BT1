# [M] Vault: Anyone can deposit to safety module to earn a higher yield

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1005-L1007
Type: audit-issue

## Details
# Vault: Anyone can deposit to safety module to earn a higher yield

## Summary

Anyone can deposit to safety module. If safety module has a higher share percentage, some users may deposit to safety module to earn a higher yield. They can monitoring the Vault to exit early to prevent taking the lose of bad debt.

## Vulnerability Detail

There is no restrictions on who can deposit to safety module.

`safety_module_interest_share_percentage` controls the percentage safety module LPs can take.

If the percentage is higher than 50%, LP can earn a higher yield in the safety module. This is true in the test cases where they have a percentage of 60%.

```python
def test_fee_is_distributed(vault, owner, weth, usdc):
    ....
    assert vault.safety_module_interest_share_percentage() == 6000 # 60%
```

## Impact

LPs can gaming on the LP dividend.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1005-L1007

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L767-L781

## Tool used

Manual Review

## Recommendation

Set restrictions on who can deposit to safety module or make sure safety module doesn't get share percentage higher than 50%.
