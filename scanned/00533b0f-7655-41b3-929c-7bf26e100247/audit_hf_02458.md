# [M] Improved cook() Logic in CauldronV4

## Summary
Severity: Medium
Contest weight: 0.4607
Dataset id: 13166
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function cook(
    uint8[] calldata actions,
    uint256[] calldata values,
    bytes[] calldata datas
) external payable returns (uint256 value1, uint256 value2) {
    CookStatus memory status;
    for (uint256 i = 0; i < actions.length; i++) {
        uint8 action = actions[i];
        if (!status.hasAccrued && action < 10) {
            accrue();
            Public
            status.hasAccrued = true;
        }
        if (action == ACTION_ADD_COLLATERAL) {
            (int256 share, address to, bool skim) = abi.decode(datas[i], (int256, address, bool));
            addCollateral(to, skim, _num(share, value1, value2));
        } else if (action == ACTION_REPAY) {
            (int256 part, address to, bool skim) = abi.decode(datas[i], (int256, address, bool));
            _repay(to, skim, _num(part, value1, value2));
        } else if (action == ACTION_REMOVE_COLLATERAL) {
            (int256 share, address to) = abi.decode(datas[i], (int256, address));
            _removeCollateral(to, _num(share, value1, value2));
            status.needsSolvencyCheck = true;
        } else if (action == ACTION_BORROW) {
            (int256 amount, address to) = abi.decode(datas[i], (int256, address));
            (value1, value2) = _borrow(to, _num(amount, value1, value2));
            status.needsSolvencyCheck = true;
        } else if (action == ACTION_UPDATE_EXCHANGE_RATE) {
            (bool must_update, uint256 minRate, uint256 maxRate) = abi.decode(datas[i], (bool, uint256, uint256));
            (bool updated, uint256 rate) = updateExchangeRate();
            require((!must_update || updated) && rate > minRate && (maxRate == 0 || rate < maxRate), "Cauldron: rate not ok");
        } else if (action == ACTION_BENTO_SETAPPROVAL) {
            (address user, address _masterContract, bool approved, uint8 v, bytes32 r, bytes32 s) = abi.decode(datas[i], (address, address, bool, uint8, bytes32, bytes32));
            bentoBox.setMasterContractApproval(user, _masterContract, approved, v, r, s);
        }
        ...
    }
}
```

## Recommendation
Revise the above routine to ensure two specific actions of ACTION_UPDATE_EXCHANGE_RATE and ACTION_BENTO_SETAPPROVAL are properly handled.
