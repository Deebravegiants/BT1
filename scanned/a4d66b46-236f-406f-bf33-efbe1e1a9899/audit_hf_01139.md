# [M] DoS in wrap and unwrap

## Summary
Severity: Medium
Contest weight: 0.5670
Dataset id: 4841
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[FuseTokenAdapterV1.sol#L76](https://github.com/code-423n4/2022-05-alchemix/blob/de65c34c7b6e4e94662bf508e214dcbf327984f4/contracts-full/adapters/fuse/FuseTokenAdapterV1.sol#L76)  
[FuseTokenAdapterV1.sol#L98](https://github.com/code-423n4/2022-05-alchemix/blob/de65c34c7b6e4e94662bf508e214dcbf327984f4/contracts-full/adapters/fuse/FuseTokenAdapterV1.sol#L98)  

The code is doing wrong check, so when things will work it will revert.

## Proof of Concept
In the function `wrap()` there is this lines:

```solidity
if ((error = ICERC20(token).mint(amount)) != NO_ERROR) {
    revert FuseError(error);
}
```

but `mint` returns the amount that minted, so when `error = amount` the check will fail even though it worked good.

Same in `unwrap`:

```solidity
if ((error = ICERC20(token).redeem(amount)) != NO_ERROR) {
    revert FuseError(error);
}
```

the redeem returns the amount.

## Recommendation
I recommend to change the lines like this: in wrap: `if ((error = ICERC20(token).mint(amount)) != amount) { revert FuseError(error); }` and in unwrap: `if ((error = ICERC20(token).redeem(amount)) != amount) { revert FuseError(error); }`

This would not cause any loss of user funds because the deposit function would revert, but it is a needed fix in the Fuse Adapter. So recommend a lower severity.

As no assets are at risk, medium risk seems correct because only the availability of the protocol is impacted.
