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
        uint256 invested = (shares * pricePerShare) / (10 ** vault.decimals());
        uint256 queued = wrappedNative.balanceOf(address(this));
        return queued + invested;
    }
```

The value of a share is computed as `pricePerShare` (which as I'll show doesn't include the locked profits)

YearnVaults compute `pricePerShare` as follows:
https://github.com/yearn/yearn-vaults/blob/97ca1b2e4fcf20f4be0ff456dabd020bfeb6697b/contracts/Vault.vy#L942-L956

```python
@view
@internal
def _shareValue(shares: uint256) -> uint256:
    # Returns price = 1:1 if vault is empty
    if self.totalSupply == 0:
        return shares

    # Determines the current value of `shares`.
    # NOTE: if sqrt(Vault.totalAssets()) >>> 1e39, this could potentially revert

    return (
        shares
        * self._freeFunds()
        / self.totalSupply
    )
```

[Where `_freeFunds()` is the difference between `_totalAssets` and a linearly unlocking value `_calculateLockedProfit`](https://github.com/yearn/yearn-vaults/blob/97ca1b2e4fcf20f4be0ff456dabd020bfeb6697b/contracts/Vault.vy#L844-L847C63)


https://github.com/yearn/yearn-vaults/blob/97ca1b2e4fcf20f4be0ff456dabd020bfeb6697b/contracts/Vault.vy#L829C1-L842C17

```python
@view
@internal
def _calculateLockedProfit() -> uint256:
    lockedFundsRatio: uint256 = (block.timestamp - self.lastReport) * self.lockedProfitDegradation

    if(lockedFundsRatio < DEGRADATION_COEFFICIENT):
        lockedProfit: uint256 = self.lockedProfit
        return lockedProfit - (
                lockedFundsRatio
                * lockedProfit
                / DEGRADATION_COEFFICIENT
            )
    else:        
        return 0

```

These profits are linearly "streamed" as the time has passed from the previous harvest

This is not done by the `YearnStartegy` which will underprice the PricePerShare (pps) by the value that corresponds to `_calculateLockedProfit`

This creates a MEV opportunity for depositors, that can:
- Deposit funds somewhere else to earn yield
- Wait for the YearnStrategy to `harvest`
- Deposit funds as the harvest happens (since pps will not appreciate)
- Withdraw as soon as the `profitDegradation` is done

Stealing the yield from honest / idle depositors


### Mitigation

Consider porting over the math around profit degradation and applying it to pricing the deposit token


### Additional info

From the Yearn Side this is something they track and they can change the `profitDegradation` as a way to avoid having people quickly steal the yield without contributing to it

From your end, it may be worth monitoring the strategy to determine if people are arbitrating it, if they are, you may chose to add an additional `profitDegradation` from your side, as a way to release the profits slowly to ensure they are split amongst those that contribute to the yield


## Assessed type

ERC4626
