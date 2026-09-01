# [M] `YearnStrategy` is ignoring the `lockedProfits`, giving away all of the Yield to laggard depositors

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1459
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/yearn/YearnStrategy.sol#L111-L117
https://github.com/yearn/yearn-vaults/blob/97ca1b2e4fcf20f4be0ff456dabd020bfeb6697b/contracts/Vault.vy#L942-L956


# Vulnerability details

Yield Farming Vaults have a known vulnerability which consists of front-running the yield distribution as a way to receive a boost in yield without contributing to it.

The way YieldBox strategies have addressed this is by adding the Pending Harvest to `_currentBalance`

Yearn Vaults instead have opted to unlock profits from an Harvest over time.

This mechanism is handled by two variables in the Yearn.Vault:
- `lockedProfit`
- `lockedProfitDegradation`

https://github.com/yearn/yearn-vaults/blob/97ca1b2e4fcf20f4be0ff456dabd020bfeb6697b/contracts/Vault.vy#L241-L242

```python
lockedProfit: public(uint256) # how much profit is locked and cant be withdrawn
lockedProfitDegradation: public(uint256) # rate per block of degradation. DEGRADATION_COEFFICIENT is 100% per block
```

When Yearn performs an harvest, it doesn't increase the PPFS by the whole amount, it instead queues these profits in the `lockedProfits`


This is where the `YearnStrategy` is leaking value

The way Yearn Strategy computes it's balance is as follows: 

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/yearn/YearnStrategy.sol#L111-L117

```solidity
    function _currentBalance() internal view override returns (uint256 amount) {
        uint256 shares = vault.balanceOf(address(this));
        uint256 pricePerShare = vault.pricePerShare();
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1459_
