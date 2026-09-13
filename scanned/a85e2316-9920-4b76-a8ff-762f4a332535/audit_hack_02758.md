# [M] TrueFi deposit can revert

## Summary
Severity: Medium
Reporter: cccz
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/main/audits/Sherlock%20-%20Trail%20of%20Bits%20Fix%20Review%20June%202022.pdf.
Type: audit-issue

## Details
# TrueFi deposit can revert

## Summary
TrueFi deposit can revert
## Vulnerability Detail
Similar to ID-5 in https://github.com/sherlock-protocol/sherlock-v2-core/blob/main/audits/Sherlock%20-%20Trail%20of%20Bits%20Fix%20Review%20June%202022.pdf.
In order to use the TrueFi strategy, a user must join the TrueFiPool to get tfUSDC by calling tfUSDC.join. However, the joiningNotPaused modifier can cause the tfUSDC.join to revert. If the owner of TrueFiPool set pauseStatus to true, then it will be impossible for anyone to deposit USDC tokens, and calls to Sherlock.yieldStrategyDeposit can revert until the TrueFiStrategy is removed.
## Impact
If the owner of TrueFiPool set pauseStatus to true, then it will be impossible for anyone to deposit USDC tokens, and calls to Sherlock.yieldStrategyDeposit can revert until the TrueFiStrategy is removed.
## Code Snippet
```solidity
  function _deposit() internal override whenNotPaused {
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L469
    tfUSDC.join(want.balanceOf(address(this)));
...
    function join(uint256 amount) external override joiningNotPaused {
...
    modifier joiningNotPaused() {
        require(!pauseStatus, "TrueFiPool: Joining the pool is paused");
        _;
    }
...
    function setPauseStatus(bool status) external override onlyOwner {
        pauseStatus = status;
        emit PauseStatusChanged(status);
    }
```
## Tool used

Manual Review

## Recommendation
Check tfUSDC.pauseStatus before tfUSDC.join, if it is true, return directly.
```diff
  function _deposit() internal override whenNotPaused {
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L469
+  if(tfUSDC.pauseStatus) return;
    tfUSDC.join(want.balanceOf(address(this)));
```
