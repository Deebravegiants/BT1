# [M] Unchecked return value when withdrawing the underlying asset from aave might result in stuck `aTokens` in `AaveHub` contract

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-08
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/7
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xa329bca26cdbfb9bbedfe14275215e91c306ad2fbbb8f0574dd71ad42a59c46c
**Severity:** medium

**Description:**
## Description

- `AaveHub.withdrawExactAmount` function is called by the position owner to withdraw deposited ERC20 aToken from `WiseLending`, and then withdraw the underlying from aave via `AaveHelper._wrapWithdrawExactAmount`.

- In `AaveHelper._wrapWithdrawExactAmount` function: it first calls `WISE_LENDING.withdrawOnBehalfExactAmount` to withdraw the aToken to the `AaveHub` contract address, and then calls `AAVE.withdraw` function to withdraw the underlying ERC20 to the position owner address:

```javascript
function _wrapWithdrawExactAmount(
        uint256 _nftId,
        address _underlyingAsset,
        address _underlyingAssetRecipient,
        uint256 _withdrawAmount
    )
        internal
        returns (uint256)
    {
        uint256 withdrawnShares = WISE_LENDING.withdrawOnBehalfExactAmount(
            _nftId,
            aaveTokenAddress[_underlyingAsset],
            _withdrawAmount
        );

        AAVE.withdraw(
            _underlyingAsset,
            _withdrawAmount,
            _underlyingAssetRecipient
        );

        return withdrawnShares;
    }
```


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/7_
