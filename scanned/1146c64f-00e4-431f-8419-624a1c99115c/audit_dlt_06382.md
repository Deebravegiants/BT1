# [M] Some feeTokens might get stuck in `FeeManager` contract if it's an aave lp token

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-15
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/30
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xd932d4999df7e0fe1e50b62447d2343df0fd6d557c2c4396bd4819c1d173a26a
**Severity:** medium

**Description:**
## Description

- `FeeManager.claimWiseFees` function can be called by anyone to claim all entitled fees from the `WiseLending` contract and send them to the `FeeManager` contract, where these fee tokens are aquired in form of shares from each pool.

- In `FeeManager.claimWiseFees` function:

  1. it first extracts the lending shares of the `FEE_MANAGER_NFT` of a specified pool.
  2. then these extracted shares are converted to an equivalent tokenAmount and withdrawn from the `WiseLending` contract.
  3. the `poolToken` is checked if it's an aave token (`aToken`); and if it's the case; the underlying asset of that `poolToken` is withdrawn from aave pool via `AAVE.withdraw` and asigned to the `tokenAmount`:

  ```javascript
  if (isAaveToken[_poolToken] == true) {
    underlyingTokenAddress = underlyingToken[_poolToken];

    tokenAmount = AAVE.withdraw(
      underlyingTokenAddress,
      tokenAmount,
      address(this)
    );
  }
  ```

  4. if there's no bad debt; this `tokenAmount` is distributed as incentives for incentive owners (A & B).
  5. and finally the amount of that feeToken is updated by increasing it with the final `tokenAmount` :

  ```javascript
  _increaseFeeTokens(underlyingTokenAddress, tokenAmount);
  ```

## Impact

**How could this result in a stuck `feeTokens` in the `FeeManager` contract?**

- If the `feeToken` is an aave lp token, the underlying is going to be withdrawn from aave (refer to point#3 above) and `tokenAmount` will be set to that withdrawn value, but `AAVE.withdraw` function **returns** the actual amount of the underlying asset that's returned from the operation, **where it might in some cases be less than the actual required amount**:

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

- So if the required amount is not fully withdrwan from aave; there will be a stuck `feeToken` (aave lp token) in the `FeeManager` contract; since entitled users to receive incentives (beneficials when there's no bad debt, and as incentives for repayers of bad debts) will be only able to withdraw a limit of `feeTokens[_feeToken]` amount only.

## Code Instance

[FeeManager.claimWiseFees function](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/FeeManager/FeeManager.sol#L628C5-L682C6)

```javascript
    function claimWiseFees(
        address _poolToken
    )
        public
    {
        address underlyingTokenAddress = _poolToken;

        uint256 shares = WISE_LENDING.getPositionLendingShares(
            FEE_MANAGER_NFT,
            _poolToken
        );

        if (shares == 0) {
            return;
        }

        uint256 tokenAmount = WISE_LENDING.withdrawExactShares(
            FEE_MANAGER_NFT,
            _poolToken,
            shares
        );

        if (isAaveToken[_poolToken] == true) {

            underlyingTokenAddress = underlyingToken[
                _poolToken
            ];

            tokenAmount = AAVE.withdraw(
                underlyingTokenAddress,
                tokenAmount,
                address(this)
            );
        }

        if (totalBadDebtETH == 0) {

            tokenAmount = _distributeIncentives(
                tokenAmount,
                _poolToken,
                underlyingTokenAddress
            );
        }

        _increaseFeeTokens(
            underlyingTokenAddress,
            tokenAmount
        );

        emit ClaimedFeesWise(
            underlyingTokenAddress,
            tokenAmount,
            block.timestamp
        );
    }
```

## Tool used

Manual Review.

## Recommendation

In `FeeManager.claimWiseFees` function, re-deposit any residual aave lp token that haven't been burnt (still stuck in the contract when withdrawing via `AAVE.withdraw`) in `WiseLending` on behalf of `FEE_MANAGER_NFT`.
