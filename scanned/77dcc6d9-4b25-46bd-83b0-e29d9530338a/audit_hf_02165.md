# [M] Incorrect roundROX() Logic in Migrator

## Summary
Severity: Medium
Contest weight: 0.4224
Dataset id: 12082
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Migrator provides users the ability to migrate their old FEG to the new one. It accepts the old FEG tokens that are directly held by users or staked in the FEGstake/FEGstakeV2 contracts. In order to facilitate users migration, it provides two ways for users to migrate their tokens. Firstly, users can migrate their FEG tokens on hand or staked in the FEGstake/FEGstakeV2 contracts separately. Secondly, users can migrate all their FEG tokens in one step. While examining the next approach to claim or stake the migrated new tokens, we notice the protocol enforces the need of multiple rounds and the current round calculation logic has an issue that needs to be fixed. In the following, we show the implementation of the related roundROX() routine. This routine computes the current round that is available to claim or stake the migrated new tokens. It comes to our attention that the internal if-condition should be revised as if(block.timestamp > timer + (timerROX*round)).
```solidity
function roundROX() public view returns(uint256 round) {
    round = 1;
    for(uint256 i = 0; i < 26; i++) {
        if(block.timestamp > timer + timerROX) {
            round += 1;
            if(round == 25) {
                break; // failsafe
            }
        }
    }
}
```

## Recommendation
Properly revise the roundROX() to compute the correct round number.
