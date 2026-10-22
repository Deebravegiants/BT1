# [M] Protocol could be DOS by transfer error due

## Summary
Severity: Medium
Contest weight: 0.6054
Dataset id: 22983
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol could be DOS due to inadequate handling of transfer errors as it does not perform code length check. As a result, many critical features such as deposit, redemption, and liquidation will be broken, leading to assets being stuck or lost of assets. ensure that the error does not prevent normal vault operations from working. This is crucial because many critical features such as deposit, redemption, and liquidation will revert if the error is not handled properly, which could lead to assets being stuck or loss of assets.
-vaults-private/contracts/vaults/common/VaultRewarderLib.sol#L316
File: VaultRewarderLib.sol
```solidity
if (0 < rewardToClaim) {
    // Ignore transfer errors here so that any strange failures here do not
    // prevent normal vault operations from working. Failures may include a
    // lack of balances or some sort of blacklist that prevents an account
    // from receiving tokens.
    try IEIP20NonStandard(rewardToken).transfer(account, rewardToClaim) {
        bool success = TokenUtils.checkReturnCode();
        if (success) {
            emit VaultRewardTransfer(rewardToken, account, rewardToClaim);
        } else {
            emit VaultRewardTransfer(rewardToken, account, 0);
        }
        // Emits zero tokens transferred if the transfer fails.
    } catch {
        emit VaultRewardTransfer(rewardToken, account, 0);
    }
}
```
Line 326 above attempts to mitigate the transfer error by "wrapping" the transfer call within the try-catch block. If the transfer function reverts, it will not revert the entire transaction and break the critical features of the protocol. However, this approach was found to be insufficient to mitigate all cases of transfer error. There is still an edge case where an error could occur during transfer, reverting the entire transaction. If the rewardToken points to an address that does not contain any code (codesize == 0), the transaction will revert instead of going into the try-catch block due to how Solidity works. It is possible that some reward tokens may contain self-destruct feature for certain reasons, resulting in the codesize becoming zero at some point in time. If the edge case occurs, many critical features such as deposit, redemption, and liquidation will be broken, leading to assets being stuck or lost of assets.

## Recommendation
Ensure that the transfer error does not revert the entire transaction under any circumstance. Consider implementing the following changes:
```solidity
if (0 < rewardToClaim) {
    // Ignore transfer errors here so that any strange failures here do not
    // prevent normal vault operations from working. Failures may include a
    // lack of balances or some sort of blacklist that prevents an account
    // from receiving tokens.
    if (rewardToken.code.length > 0) {
        try IEIP20NonStandard(rewardToken).transfer(account, rewardToClaim) {
            bool success = TokenUtils.checkReturnCode();
            if (success) {
                emit VaultRewardTransfer(rewardToken, account, rewardToClaim);
            } else {
                emit VaultRewardTransfer(rewardToken, account, 0);
            }
            // Emits zero tokens transferred if the transfer fails.
        } catch {
            emit VaultRewardTransfer(rewardToken, account, 0);
        }
    }
}
```
