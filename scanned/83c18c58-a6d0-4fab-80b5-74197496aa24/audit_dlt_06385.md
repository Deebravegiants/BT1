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

## Impact

But `AAVE.withdraw` function **returns** the actual amount of the underlying asset that's returned from the operation, **where it might in some cases be less than the actual required amount**, and if this is the case where the required amount is not fully withdrwan; this will result in **stuck residual aToken in the `AaveHub` contract**, as these tokens can't be withdrawn or utilized:

[aave.IPool.withdraw](https://github.com/aave/aave-v3-core/blob/6070e82d962d9b12835c88e68210d0e63f08d035/contracts/interfaces/IPool.sol#L276C1-L287C91)

```javascript
  /**
* @notice Withdraws an `amount` of underlying asset from the reserve, burning the equivalent aTokens owned
* E.g. User has 100 aUSDC, calls withdraw() and receives 100 USDC, burning the 100 aUSDC
* @param asset The address of the underlying asset to withdraw
* @param amount The underlying amount to be withdrawn
*   - Send the value type(uint256).max in order to withdraw the whole aToken balance
* @param to The address that will receive the underlying, same as msg.sender if the user
*   wants to receive it on his own wallet, or a different address if the beneficiary is a
*   different wallet
* @return The final amount withdrawn
*/
function withdraw(address asset, uint256 amount, address to) external returns (uint256);
```

- Same issue with `_wrapWithdrawExactShares` and `_wrapBorrowExactAmount` functions.

## Code Instance

[AaveHub.withdrawExactAmount function](https://github.com/wise-foundation/lending-audit/blob/7482c9fd1a27629e87a248c818758445fce6101a/contracts/WrapperHub/AaveHub.sol#L216C4-L221C11)

```javascript
        uint256 withdrawnShares = _wrapWithdrawExactAmount(
            _nftId,
            _underlyingAsset,
            msg.sender,
            _withdrawAmount
        );
```

[AaveHelper.\_wrapWithdrawExactAmount function](https://github.com/wise-foundation/lending-audit/blob/7482c9fd1a27629e87a248c818758445fce6101a/contracts/WrapperHub/AaveHelper.sol#L79C5-L101C6)

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

## Tool used

Manual Review

## Recommendation

In `AaveHub.withdrawExactAmount` function, if there's any residual `aTokens` than hasn't been burnt (still stuck in the contract) when withdrawing via `AAVE.withdraw`:
either transfer these tokens to the position owner, or re-deposit them again in `WiseLending`.

```diff
    function withdrawExactAmount(
        uint256 _nftId,
        address _underlyingAsset,
        uint256 _withdrawAmount
    ) external nonReentrant validToken(_underlyingAsset) returns (uint256) {
        _checkOwner(_nftId);
+       address aaveToken = aaveTokenAddress[_underlyingAsset];
+       uint256 balanceBefore = aaveToken.balanceOf(address(this));

        uint256 withdrawnShares = _wrapWithdrawExactAmount(
            _nftId,
            _underlyingAsset,
            msg.sender,
            _withdrawAmount
        );
+       uint256 balanceAfter = aaveToken.balanceOf(address(this));
        emit IsWithdrawAave(_nftId, block.timestamp);
+       if(balanceAfter > balanceBefore){
+           _safeTransferFrom(aaveToken, address(this), msg.sender,  balanceAfter - balanceBefore);
+       }
        return withdrawnShares;
    }
```
