# [C] Winner can withdraw deposit after winning

## Summary
Severity: Critical
Contest weight: 0.4196
Dataset id: 3957
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The lotteries in this protocol work in such a way that ticket buyers compete to have a chance to buy an NFT for the deposit they've provided. The proceeds from these NFTs can then be collected by the seller minus a protocol tax. In Deposit.sol buyers buy tickets, then when the seller is satisfied with the amount of buyers, they start the lottery by calling startLottery followed by initiateSelectWinner. This will request randomness from the VRF. Once randomness is returned the seller calls selectWinners where the winners will be selected using the randomness provided. The issue is that during the time between that the randomness is fulfilled in fulfillRandomWords and the seller calls selectWinners the buyer will know if they've won and can withdraw their deposit. Since the buyer is already added to the eligibleParticipants from when startLottery was called. They would still be able to win. Hence the buyer would get the NFT without paying.

## Proof of Concept
Add this test to Deposit.t.sol:
```solidity
function test_WinnerWithdrawAfterRandomnessIsFulfulled() public {
    uint256 depositAmount = 1 ether;
    vm.deal(winner, depositAmount);
    vm.prank(winner);
    deposit.deposit{value: depositAmount}();
    // seller starts lottery
    vm.startPrank(seller);
    deposit.setNumberOfTickets(1);
    deposit.startLottery();
    uint256 requestId = deposit.initiateSelectWinner();
    vm.stopPrank();
    // VRF returns with randomness
    vm.mockVRFResponse(requestId, 1);
    // winner sees that they won and withdraws their deposit
    vm.prank(winner);
    deposit.buyerWithdraw();
    // seller sets winner
    vm.startPrank(seller);
    deposit.selectWinners();
    deposit.endLottery();
    deposit.sellerWithdraw();
    vm.stopPrank();
    // winner both won and have their deposit
    assertEq(winner.balance, 1 ether);
    assertEq(deposit.isWinner(winner), true);
    // seller got nothing
    assertEq(seller.balance, 0);
}
```

## Recommendation
Consider only letting buyers withdraw after the lottery has ended:
```solidity
function buyerWithdraw() public whenLotteryNotActive {
function buyerWithdraw() public lotteryEnded {
```
