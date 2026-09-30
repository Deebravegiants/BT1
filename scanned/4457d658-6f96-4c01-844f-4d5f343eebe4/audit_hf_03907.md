# [M] SimpleRamp will not burn any excess iFIL it

## Summary
Severity: Medium
Contest weight: 0.1365
Dataset id: 20206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If any excess iFIL is sent to SimpleRamp, it will not be burned, although it is supposed to do so. to burn any excess iFIL sent to the address in order to prevent from accounting issues. // this contract will burn any excess iFIL it has (this shouldn't happen, but in case it does, we dont have accounting issues)
uint256 balanceOfBefore = iFIL.balanceOf(address(this));
// pull in the iFIL from the iFIL holder, which will decrease the allowance of this ramp to spend on behalf of the iFIL holder
iFIL.transferFrom(owner, address(this), iFILToBurn);
// burn the exiter's iFIL tokens (and any additional iFIL tokens that somehow ended up here)
iFIL.burn(
    address(this),
    iFIL.balanceOf(address(this)) - balanceOfBefore
);
However, the current implementation burns just the amount of iFIL the user has sent, potentially causing accounting issues. Contract doesn't work as expected. Potential accounting issues.

## Recommendation
Change the burn line of code to the following iFIL.burn(address(this), iFIL.balanceOf(address(this)));
