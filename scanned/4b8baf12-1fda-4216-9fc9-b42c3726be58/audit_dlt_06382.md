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

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/30_
