# [C] IncorrectReceiverof Extraspins andGPointsin _handlePayout()

## Summary
Severity: Critical
Contest weight: 0.8337
Dataset id: 8612
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `_handleRewardPayout()` function is called by `fulfillRandomWords()` which is called by `rawFulfillRandomWords()` in the `VRFConsumerBaseV2Plus` contract. The permissions to call `rawFulfillRandomWords()` is only granted to the `vrfCoordinator`, thus the `msg.sender` can never be the user that needs to receive the extra spins as a reward. The code in the `_handleRewardPayout()` for extra spins and gPoints assigns the spins and points to `msg.sender`.

The rewarded extra spins are given to the caller which is the VRFConsumerBaseV2Plus contract.

## Proof of Concept
```solidity
function test_IncorrectAssignSpins() external {
    setConfig();
    vm.prank(veOwner);
    MockWheelOfGuantune(wheelproxy).giveExtraSpins(User1, 1);
    uint256 availableSpins = MockWheelOfGuantune(wheelproxy).getAvailableSpinsOf(User1);
    console.log("Number of spins avaialble for User1 before first spin : %d", availableSpins);
    vm.prank(User1);
    uint256 vrfRequestId = MockWheelOfGuantune(wheelproxy).spin();
    WheelOfGuantune.SpinRequest memory request = MockWheelOfGuantune(wheelproxy).getSpinRequest(vrfRequestId);
    assertEq(request.user, User1);
    assertFalse(request.isFulfilled);

    availableSpins = MockWheelOfGuantune(wheelproxy).getAvailableSpinsOf(User1);
    console.log("Number of spins avaialble for User1 after first spin : %d", availableSpins);
    availableSpins = MockWheelOfGuantune(wheelproxy).getAvailableSpinsOf(address(mockVRF));
    console.log("Number of spins avaialble for mockVRF before fulfil call : %d", availableSpins);
    mockVRF.doCallBack(wheelproxy, vrfRequestId);
    request = MockWheelOfGuantune(wheelproxy).getSpinRequest(vrfRequestId);
    assertEq(request.user, User1);
    assertTrue(request.isFulfilled);
    availableSpins = MockWheelOfGuantune(wheelproxy).getAvailableSpinsOf(address(mockVRF));
    console.log("Number of spins avaialble for mockVRF after fulfil call : %d", availableSpins);
}
```
Gives output of:
[PASS] test_IncorrectAssignSpins() (gas: 626235)
Logs:
Number of spins avaialble for User1 before first spin : 1
Number of spins avaialble for User1 after first spin : 1
Number of spins avaialble for mockVRF before fulfil call : 0
Number of spins avaialble for mockVRF after fulfil call : 1

## Recommendation
Consider applying the following changes:
```solidity
} else if (rewardType == RewardType.ExtraSpins) {
    // fetch the extra spins amount of the reward id
    uint256 extraSpins = $.config.extraSpinsOfRewardId[$.config.extraSpinsOfRewardId.length - 1].get(rewardId);
    // update the user's extra spins balance and store the abi-encoded reward value
    // $.extraSpinsOfUser[msg.sender] += extraSpins;
    $.extraSpinsOfUser[user] += extraSpins;
    rewardValue = abi.encode(extraSpins);
} else if (rewardType == RewardType.GPoints) {
    // fetch the gPoints amount of the reward id
    uint256 gPoints = $.config.gPointsOfRewardId[$.config.gPointsOfRewardId.length - 1].get(rewardId);
    // update the user's gPoints balance
    // $.gPointsOfUser[msg.sender] += gPoints;
    $.gPointsOfUser[user] += gPoints;
    // update the total gPoints
}
```
