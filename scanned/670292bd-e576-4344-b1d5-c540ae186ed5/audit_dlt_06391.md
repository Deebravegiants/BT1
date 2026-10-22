# [M] In some cases, the redemption process in the Repricing Token may be reverted.

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-03-03
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/55
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x839d3b9407ba3e1651355153306a5eb7624144d6ba9cedddf4aaca484ea2eb5f
**Severity:** medium

**Description:**
**Description**\
In the `Repricing Token`, there are `vested reserves` and `pending reserves`.
When calculating `shares` from `reserves`, or vice versa, we use the `vested reserves` and the `accrued pending reserves` from the `last checkpoint`.
The `redemption` amount is deducted from `vestedReserves`. 
However, `vestedReserves` are only updated when the `_checkpointAndAddReserves` function is called. 
This implies that in some cases, the `redemption` amount can exceed the `vestedReserves`.

**Attack Scenario**\
Let's consider there are `S` `shares`, `V` `vested reserves`, and no `pending reserves` at this point. 
Now, if one user wants to deposit `X` `reserve tokens`, the `shares` for this deposit (denoted as `A`) are calculated in the function below.
```
function _issueSharesFromReserves(
    uint256 reserveTokenAmount, 
    address recipient, 
    uint256 minSharesAmount
) internal returns (uint256 sharesAmount) {
    sharesAmount = reservesToShares(reserveTokenAmount);
    ...
}
function reservesToShares(uint256 reserves) public view override returns (uint256) {
    uint256 _totalSupply = totalSupply();
    return (_totalSupply == 0)
        ? reserves
        : reserves.mulDiv(_totalSupply, totalReserves(), OrigamiMath.Rounding.ROUND_DOWN);
}
```
i.e.
```
A = X * S / V
```
The `total shares` become `S + A`, and the `vestedReserves` become `V + X`.

The `rewards minter` mints some `reserve tokens` for `interest`. 
The function below will be called.
```
function addPendingReserves(uint256 amount) external override onlyElevatedAccess {
    if (amount == 0) revert CommonEventsAndErrors.ExpectedNonZero();

    emit PendingReservesAdded(amount);
    IERC20(reserveToken).safeTransferFrom(msg.sender, address(this), amount);

    _checkpointAndAddReserves(amount);
    _validateReservesBalance();
}
```
At this point, there is no change in `vestedReserves`.

After some time, the user wants to redeem his shares `A`. 
Let's suppose there are `P` `accrued pending reserves` from `last checkpoint`.
The below function is invoked.
```
function _redeemReservesFromShares(
    uint256 sharesAmount, 
    address from, 
    uint256 minReserveTokenAmount,
    address receiver
) internal returns (uint256 reserveTokenAmount) {
    if (balanceOf(from) < sharesAmount) revert CommonEventsAndErrors.InsufficientBalance(address(this), sharesAmount, balanceOf(from));

    reserveTokenAmount = sharesToReserves(sharesAmount);
    if (reserveTokenAmount == 0) revert CommonEventsAndErrors.ExpectedNonZero();
    if (reserveTokenAmount < minReserveTokenAmount) revert CommonEventsAndErrors.Slippage(minReserveTokenAmount, reserveTokenAmount);

    // Burn the users shares and remove the reserves
    _burn(from, sharesAmount);

    vestedReserves -= reserveTokenAmount;
    emit VestedReservesRemoved(reserveTokenAmount);

    if (receiver != address(this)) {
        IERC20(reserveToken).safeTransfer(receiver, reserveTokenAmount);
    }

    _validateReservesBalance();
}
```
The calculation for the `reserves` to be removed(denoted as `R`) is as follows:
```
function sharesToReserves(uint256 shares) public view override returns (uint256) {
    uint256 _totalSupply = totalSupply();

    return (_totalSupply == 0)
        ? shares
        : shares.mulDiv(totalReserves(), _totalSupply, OrigamiMath.Rounding.ROUND_DOWN);
}
```
i.e.
```
R = A * (V + X + P) / (S + A) = (X * S / V) * ((V + X + P) / (S + X * S / V)) = (X * S * (V + X + P)) / (V * S + X * S) = X * (V + X + P) / (V + X)
```
I believe there are cases where the `redemption amount` (`R`) is larger than the `vested reserves`(`V`) for certain values of `X`, `V`  and `P`.
It's easy to find specific values that satisfy the condition below.
```
X * (V + X + P) / (V + X) > V  <=>  X * V + X * X + X * P > V * V + V * X  <=>  X * X + X * P > V * V
```
 This implies that the `redemption` will be reverted even though all calculations are correct and there are enough `reserve tokens` to `redeem` in the `Repricing token`. 
I marked this a `medium` as it is a kind of DoS scenario.
**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
We can mitigate this issue by calling the `_checkpointAndAddReserves` function when the `vestedReserves` are less than the amount to be redeemed. 
The frequency of calling this function will be minimal, so there will be no any potential risks associated with this fix.
```
function _redeemReservesFromShares(
    uint256 sharesAmount, 
    address from, 
    uint256 minReserveTokenAmount,
    address receiver
) internal returns (uint256 reserveTokenAmount) {
    if (balanceOf(from) < sharesAmount) revert CommonEventsAndErrors.InsufficientBalance(address(this), sharesAmount, balanceOf(from));

    reserveTokenAmount = sharesToReserves(sharesAmount);
    if (reserveTokenAmount == 0) revert CommonEventsAndErrors.ExpectedNonZero();
    if (reserveTokenAmount < minReserveTokenAmount) revert CommonEventsAndErrors.Slippage(minReserveTokenAmount, reserveTokenAmount);

    // Burn the users shares and remove the reserves
    _burn(from, sharesAmount);

+     if (vestedReserves < reserveTokenAmount) {
+         _checkpointAndAddReserves(0);
+     }

    vestedReserves -= reserveTokenAmount;
    emit VestedReservesRemoved(reserveTokenAmount);

    if (receiver != address(this)) {
        IERC20(reserveToken).safeTransfer(receiver, reserveTokenAmount);
    }

    _validateReservesBalance();
}
```
