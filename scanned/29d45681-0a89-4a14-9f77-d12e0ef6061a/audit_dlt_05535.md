# [?] fix(across): address possible underflow in bridge pool (#3624)

## Summary
Severity: Unknown
Chain: UMA
Component: UMAprotocol/protocol
Published: 2021-11-19
Source: https://github.com/UMAprotocol/protocol/commit/a01005cf08dad4f84039d6f8eeb7d14c7b730fa3
Type: security-commit

## Details
fix(across): address possible underflow in bridge pool (#3624)

* fix(across): address posible underflow in bridge pool

Signed-off-by: chrismaree <christopher.maree@gmail.com>

* nit

Signed-off-by: chrismaree <christopher.maree@gmail.com>

## Patch
### packages/core/contracts/insured-bridge/BridgePool.sol
```diff
@@ -758,10 +758,11 @@ contract BridgePool is MultiCaller, Testable, BridgePoolInterface, ERC20, Lockab
         _sync(); // Fetch any balance changes due to token bridging finalization and factor them in.
 
         // ExchangeRate := (liquidReserves + utilizedReserves - undistributedLpFees) / lpTokenSupply
-        uint256 numerator = liquidReserves - undistributedLpFees;
-        if (utilizedReserves > 0) numerator += uint256(utilizedReserves);
-        else numerator -= uint256(utilizedReserves * -1);
-        return (numerator * 1e18) / totalSupply();
+        // Note that utilizedReserves can be negative. If this is the case, then liquidReserves is offset by an equal
+        // and opposite size. LiquidReserves + utilizedReserves will always be larger than undistributedLpFees so this
+        // int will always be positive so there is no risk in underflow in type casting in the return line.
+        int256 numerator = int256(liquidReserves) + utilizedReserves - int256(undistributedLpFees);
+        return (uint256(numerator) * 1e18) / totalSupply();
     }
 
     // Return UTF8-decodable ancillary data for relay price request associated with relay hash.
```

### packages/core/test/insured-bridge/BridgePool.js
```diff
@@ -2118,6 +2118,92 @@ describe("BridgePool", () => {
       await l1Token.methods.mint(bridgePool.options.address, toWei("100")).send({ from: owner });
       assert.equal((await bridgePool.methods.exchangeRateCurrent().call()).toString(), toWei("1.01"));
     });
+    it("Edge cases cant force exchange rate current to revert", async () => {
+      // There are some extreme edge cases that can cause the exchange rate to revert in pervious versions of the smart
+      // contracts. This test aims to mimic them and show that there is no condition where this is an issue with the
+      // modified exchange rate computation logic.
+      // Create a relay that uses all liquid reserves.
+      const liquidReservesPreLargeRelay = await bridgePool.methods.liquidReserves().call();
+
+      await l1Token.methods.mint(relayer, liquidReservesPreLargeRelay).send({ from: owner });
+      await l1Token.methods.approve(bridgePool.options.address, liquidReservesPreLargeRelay).send({ from: relayer });
+
+      let requestTimestamp = (await bridgePool.methods.getCurrentTime().call()).toString();
+      await bridgePool.methods
+        .relayDeposit(...generateRelayParams({ depositId: 1, amount: liquidReservesPreLargeRelay }))
+        .send({ from: relayer });
+
+      console.log(
+        "bond",
+        toBN(liquidReservesPreLargeRelay)
+          .mul(toBN(defaultProposerBondPct))
+          .div(toBN(toWei("1")))
+          .toString()
+      );
+
+      const relayAttemptData2 = {
+        ...defaultRelayData,
+        relayId: 1,
+        priceRequestTime: requestTimestamp,
+        relayState: InsuredBridgeRelayStateEnum.PENDING,
+        proposerBond: toBN(liquidReservesPreLargeRelay)
+          .mul(toBN(defaultProposerBondPct))
+          .div(toBN(toWei("1")))
+          .toString(),
+      };
+      await advanceTime(defaultLiveness);
+      await bridgePool.methods
+        .settleRelay({ ...defaultDepositData, depositId: 1, amount: liquidReservesPreLargeRelay }, relayAttemptData2)
+        .send({ from: relayer });
+
+      // now, liquid reserves should be the realizedLP Fee from the previous relay.
+      assert.equal(
+        (await bridgePool.methods.liquidReserves().call()).toString(),
+        toBN(liquidReservesPreLargeRelay)
+          .mul(toBN(defaultRealizedLpFee))
+          .div(toBN(toWei("1")))
+          .toString()
+      );
+
+      await bridgePool.methods.exchangeRateCurrent().call(); // Exchange rate current should still work, as expected (not revert).
+
+      // Further relay the remaining liquid reserves.
+      requestTimestamp = (await bridgePool.methods.getCurrentTime().call()).toString();
+      const liquidReservesPostLargeRelay = await bridgePool.methods.liquidReserves().call();
+      await bridgePool.methods
+        .relayDeposit(...generateRelayParams({ depositId: 2, amount: liquidReservesPostLargeRelay }))
+        .send({ from: relayer });
+
+      // Now, finalize this relay.
+      const relayAttemptData3 = {
+        ...defaultRelayData,
+        relayId: 2,
+        priceRequestTime: requestTimestamp,
+        relayState: InsuredBridgeRelayStateEnum.PENDING,
+        proposerBond: toBN(liquidReservesPostLargeRelay)
+          .mul(toBN(defaultProposerBondPct))
+          .div(toBN(toWei("1")))
+          .toString(),
+      };
+
+      await advanceTime(defaultLiveness);
+      await bridgePool.methods
+        .settleRelay({ ...defaultDepositData, depositId: 2, amount: liquidReservesPostLargeRelay }, relayAttemptData3)
+        .send({ from: relayer });
+
+      // Exchange rate current should still work, as expected (not revert). Note that at this point the undistributed LP fees exceed the liquid reserves.
+      const endRate = await bridgePool.methods.exchangeRateCurrent().call();
+
+      // Mimic some funds coming over the canonical bridge by a mint. This should not affect the exchange rate.
+      await l1Token.methods.mint(bridgePool.options.address, toWei("500")).send({ from: owner });
+      assert.equal(endRate.toString(), (await bridgePool.methods.exchangeRateCurrent().call()).toString());
+
+      // Finally, dump a larger amount of tokens into the pool than was originally added by LPs. Again, this should
+      // break nothing.
+      await l1Token.methods.mint(bridgePool.options.address, toWei("1500")).send({ from: owner });
+      await bridgePool.methods.exchangeRateCurrent().call();
+      assert.equal(endRate.toString(), (await bridgePool.methods.exchangeRateCurrent().call()).toString());
+    });
   });
   describe("Liquidity utilization rato", () => {
     beforeEach(async function () {
```
