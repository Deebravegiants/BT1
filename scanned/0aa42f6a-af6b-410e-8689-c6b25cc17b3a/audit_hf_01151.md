# [M] retainerc4626 ﬂag mishandling in _updatemultideposit

## Summary
Severity: Medium
Reporter: elhaj
Contest weight: 0.6446
Dataset id: 4912
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After cross-chain multideposit arrives to the coreStateRegistry, the keeper will update the deposit first, before processing it through updateDepositPayload().
```solidity
function updateDepositPayload(uint256 payloadId_, uint256[] calldata finalAmounts_) external virtual override {
    _onlyAllowedCaller(keccak256("CORE_STATE_REGISTRY_UPDATER_ROLE"));
    // some code ...
    PayloadState finalState;
    if (isMulti != 0) {
        // See the line below
        (prevPayloadBody, finalState) = _updateMultiDeposit(payloadId_, prevPayloadBody, finalAmounts_);
    } else {
        // this will may or may not update the amount n prevPayloadBody .
        (prevPayloadBody, finalState) = _updateSingleDeposit(payloadId_, prevPayloadBody, finalAmounts_[0]);
    }
    // some code ...
}
```
In this case, the _updateMultiDeposit function is responsible for updating the deposit payload by resolving the final amounts given by the keeper. In this process, the failed deposits will be removed from the payload body and set to failedDeposit to be rescued later by the user.
```solidity
function _updateMultiDeposit(
    uint256 payloadId_,
    bytes memory prevPayloadBody_,
    uint256[] calldata finalAmounts_
)
    internal
    returns (bytes memory newPayloadBody_, PayloadState finalState_)
{
    /// some code ...
    uint256 validLen;
    for (uint256 i; i < arrLen; ++i) {
        if (finalAmounts_[i] == 0) {
            revert Error.ZERO_AMOUNT();
        }
        // update the amounts :
        (multiVaultData.amounts[i],, validLen) = _updateAmount(
            dstSwapper,
            multiVaultData.hasDstSwaps[i],
            payloadId_,
            i,
            finalAmounts_[i],
            multiVaultData.superformIds[i],
            multiVaultData.amounts[i],
            multiVaultData.maxSlippages[i],
            finalState_,
            validLen
        );
    }
    // update the payload body and remove the failed deposits
    if (validLen != 0) {
        uint256[] memory finalSuperformIds = new uint256[](validLen);
        uint256[] memory finalAmounts = new uint256[](validLen);
        uint256[] memory maxSlippage = new uint256[](validLen);
        bool[] memory hasDstSwaps = new bool[](validLen);
        uint256 currLen;
        for (uint256 i; i < arrLen; ++i) {
            if (multiVaultData.amounts[i] != 0) {
                finalSuperformIds[currLen] = multiVaultData.superformIds[i];
                finalAmounts[currLen] = multiVaultData.amounts[i];
                maxSlippage[currLen] = multiVaultData.maxSlippages[i];
                hasDstSwaps[currLen] = multiVaultData.hasDstSwaps[i];
                ++currLen;
            }
        }
        multiVaultData.amounts = finalAmounts;
        multiVaultData.superformIds = finalSuperformIds;
        multiVaultData.maxSlippages = maxSlippage;
        multiVaultData.hasDstSwaps = hasDstSwaps;
        finalState_ = PayloadState.UPDATED;
    } else {
        finalState_ = PayloadState.PROCESSED;
    }
    // return new payload
    newPayloadBody_ = abi.encode(multiVaultData);
}
```
The problem arises when some deposits fail and others succeed. The function doesn't update the retainERC4626 flags to match the new state: This misalignment can lead to incorrect minting behavior in the _multiDeposit function, where the retainERC4626 flags do not correspond to the correct superFormsIds.

## Proof of Concept
1. Bob creates a singleXchainMultiDeposit with its corresponding data:
• superFormsIds[1,2,3,4]
• amounts[a,b,c,d]
• retainERC4626[true,true,false,false]
2. After the cross-chain payload is received and all is good, a keeper comes and updates the amounts. Assuming the update of amounts resulted in a and b failing, while c and d are resolved successfully.
3. The _updateMultiDeposit function updates the payload to contain:
• superFormsIds[3,4]
• amounts[c',d']
• retainERC4626[true,true,false,false]
3. Here, retainERC4626 is not updated. So, when the keeper processes the payload, _multiDeposit is triggered, and Bob is incorrectly minted superPositions for superForms 3 and 4, despite the user's preference to retain ERC4626 shares for these superForms. Therefore, the issue can lead to incorrect minting or unminting behavior of superPositions, where users may receive superPositions when they intended to retain ERC4626 shares, or vice versa. While it may be not a big issue for EOAs, this can be particularly problematic for contracts integrating with Superform, potentially breaking invariants and causing loss of funds.

## Recommendation
No data
