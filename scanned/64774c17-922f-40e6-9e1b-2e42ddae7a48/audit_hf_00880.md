# [M] Setting peripheryFlashLoanFee does not

## Summary
Severity: Medium
Contest weight: 0.7599
Dataset id: 2636
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In DebtToken when flashloan is initiated the _flashFee() function is used to determine the effective fee:
```solidity
function _flashFee(uint256 amount) internal view returns (uint256) {
    uint effectiveFee = _beraborrowCore.getPeripheryFlashLoanFee(msg.sender);
    return (amount * effectiveFee) / 1e4;
}
```
However, because the getPeripheryFlashLoanFee() function is called on the BeraborrowCore contract, the msg.sender in MetaBeraborrowCore, where the peripheryFlashLoanFee is set, will not pass the check:
```solidity
if (msg.sender == nect) {
    if (info.existsForNect) {
        return info.nectFee;
    }
}
```
always returning the DEFAULT_FLASH_LOAN_FEE. getPeripheryFlashLoanFee incorrectly checks the msg.sender value and the DebtToken contract calls BeraborrowCore instead of MetaBeraborrowCore. aBeraborrowCore.sol#L178-L182 Internal Pre-conditions External Pre-conditions Attack Path It is impossible to implement a flashloan fee reduction/increase for any periphery contract.

## Proof of Concept
Place the following test in DebtToken.t.sol:
```solidity
function test_getPeripheryFlashLoanFee() public {
    uint16 newFee = 1; // 0.05% --> 0.01%
    address periphery = makeAddr("periphery");
    vm.prank(owner);
    metaBeraborrowCore.setPeripheryFlashLoanFee(periphery, newFee, true);
    vm.prank(periphery);
    uint fee = nectarToken.flashFee(address(nectarToken), 1e4);
    assertEq(fee , 5);
}
```

## Recommendation
Make the following change in getPeripheryFlashLoanFee():
```solidity
if (msg.sender == nect) {
    if (info.existsForNect) {
        return info.nectFee;
    }
}
```
To support calling that method through BeraborrowCore first or MetaBeraborrowCore directly.
