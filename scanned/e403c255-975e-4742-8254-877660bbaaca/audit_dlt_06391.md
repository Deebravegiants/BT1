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


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/55_
