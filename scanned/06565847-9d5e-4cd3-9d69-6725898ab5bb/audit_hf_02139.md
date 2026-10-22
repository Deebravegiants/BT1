# [M] Improved WETH Input Amount in _adjustArray()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12004
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERD allows a user to open a Trove to borrow USDE by supplying required collateral. The first token to be supported as collateral is WETH. To facilitate users supply WETH, the protocol allows users to take ETH (msg.value) within the transactions to open troves. The ETH will be deposited to WETH by ERD on behalf of the borrower. While examining the calculation of the WETH amount to be supplied, we notice the WETH amount may not be correctly counted. In the following, we show the code snippet of the _adjustArray() routine which is used to count the input WETH amount in all the input collaterals. By design, if msg.value > 0, it shall check if WETH exists in the input collateral list or not. If WETH doesn't exist, it adds WETH into the collateral list with msg.value as its amount. Otherwise, it adds msg.value to the amount of WETH. However, it comes to our attention that, when WETH exists in the input collateral list, the current implementation tries to update the corresponding collateral address from WETH to a wrong one (line 323). As a result, the input collaterals are messed up. Based on this, we suggest to update the input amount of WETH only when WETH exists in the input collateral list.
```solidity
function _adjustArray(
    address[] memory _collaterals,
    uint256[] memory _amounts,
    uint256 _amount
) public view returns (
    address[] memory,
    uint256[] memory
) {
    uint256 collLen = _collaterals.length;
    if (collLen == 0 && _amount > 0) { ... }
    if (_amount > 0) {
        address[] memory collaterals = new address[](collLen + 1);
        uint256[] memory amounts = new uint256[](collLen + 1);
        collaterals[0] = address(WETH);
        amounts[0] = _amount;
        address collateral;
        bool hasWETH;
        uint256 index;
        for (uint256 i = 0; i < collLen; i++) {
            collateral = _collaterals[i];
            if (collateral != address(WETH)) {
                collaterals[i + 1] = collateral;
                amounts[i + 1] = _amounts[i];
            } else {
                hasWETH = true;
                index = i;
                break;
            }
        }
        if (hasWETH) {
            _collaterals[index] = _collaterals[index].add(_amount);
        }
        return (_collaterals, _amounts);
    } else {
        return (_collaterals, _amounts);
    }
}
```

## Recommendation
Revisit the above _adjustArray() routine and correctly update the input amount of WETH.
