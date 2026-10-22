# [M] Auction.getEpochsByBuyer can be broken

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L429-L446
Type: audit-issue

## Details
# Auction.getEpochsByBuyer can be broken

## Summary
`Auction.getEpochsByBuyer` function will not work correctly if user created few orders for the same epoch and then canceled 1 order.

## Vulnerability Detail
`Auction.getEpochsByBuyer` [function](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L429-L446) is used to show in which epochs user has orders.

When you create new limit order(for example) then `_addOrder` function is [called](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L179). This function the [add](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L553) current epoch to the user.

Also we have `cancelLimitOrder` [function](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L205-L230) which takes order id and then [removes](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L220) epoch for the sender.

In case when user created more then 1 order and then canceled 1 of them, then the epoch will be removed for him and the `Auction.getEpochsByBuyer` function will not return that epoch, however user still has orders there.
## Impact
UI or someone else will use the wrong results from `Auction.getEpochsByBuyer` function.
## Code Snippet
The test below can be runned in `Auction.behaviour.ts` file. It creates 2 limit orders for user and then remove 1 of them. The epochs by user are empty, but we still have 1 order.

```javascript
describe("if auction has not started", () => {
        let endTime: BigNumber;
        let epoch: BigNumber;

        time.revertToSnapshotAfterEach(async () => {
          [, endTime, epoch] = await knoxUtil.initializeAuction();
          await asset
            .connect(signers.buyer1)
            .approve(addresses.auction, ethers.constants.MaxUint256);
        });

        it("removes epochByBuyer who has more then 1 orders", async () => {
          await asset
            .connect(signers.buyer1)
            .approve(addresses.auction, ethers.constants.MaxUint256);

            //add first order
          await auction.addLimitOrder(
            epoch,
            fixedFromFloat(params.price.max),
            params.size
          );

          let epochByBuyer = await auction.getEpochsByBuyer(addresses.buyer1);
          assert.equal(epochByBuyer.length, 1);

          //add second order
          await auction.addLimitOrder(
            epoch,
            fixedFromFloat(params.price.max),
            params.size
          );

          epochByBuyer = await auction.getEpochsByBuyer(addresses.buyer1);
          assert.equal(epochByBuyer.length, 1);

          //cancel order 1
          await auction.cancelLimitOrder(epoch, 1);
          epochByBuyer = await auction.getEpochsByBuyer(addresses.buyer1);
          assert.isEmpty(epochByBuyer);

          //we still have 1 order, but no epochs
          epochByBuyer = await auction.getEpochsByBuyer(addresses.buyer1);
          assert.isEmpty(epochByBuyer);

          //this proves that we still have this order in the epoch as we can cancel it
          await auction.cancelLimitOrder(epoch, 2);
        });
      });
      ```
## Tool used

VsCode

## Recommendation
Check if user has more orders in the epoch before removing it.
