# [H] Buyer can request randomness multiple times

## Summary
Severity: High
Contest weight: 0.9902
Dataset id: 3961
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
The issue here is that in deposit it only checks that the user doesn't have a fulfilled request. VRFs take some time to process requests. A ticket buyer could send as many requests as they can before the first one is fulfilled which will increase their changes to win. Since as long as one of the rolls succeed they'll get added to the winners list. Only the first one need to be above the minimum deposit threshold, the later ones can just be dust. Hence a buyer could get many rolls for just one ticket price.

## Proof of Concept
```solidity
function test_LotteryV2RequestRandomnessMultipleTimesDeposit() public {
    usdc.mint(alice, 2e6);
    vm.startPrank(alice);
    // first randomness request with enough to cover minimum deposit
    bytes memory data = abi.encode(0, abi.encode(alice));
    uint256 round = _round();
    bytes memory dataWithRound = abi.encode(round, data);
    emit IGelatoVRFConsumer.RequestedRandomness(round, data);
    lottery.deposit(1e6);
    // second randomness request while first is still pending for dust
    data = abi.encode(1, abi.encode(alice));
    dataWithRound = abi.encode(round, data);
    emit IGelatoVRFConsumer.RequestedRandomness(round, data);
    lottery.deposit(1);
    vm.stopPrank();
}
```
Please find the full test setup here

## Recommendation
Consider only sending a randomness request if both rolledNumbers[_msgSender()] == 0 and deposits[_msgSender()] == 0 in both LotteryV2Base::deposit and transferDeposit:
```solidity
if (deposits[_msgSender()] == 0) {
    participants.push(_msgSender());
    if (rolledNumbers[_msgSender()] == 0) {
        _requestRandomness(abi.encode(_msgSender()));
        emit RandomRequested(_msgSender());
    }
}
deposits[_msgSender()] += amount;
```
This will guarantee that only one request is sent per ticket buyer.
