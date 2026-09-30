# [?] Fix overflow bug that occasionally occurs when supplying 0 base (#455)

## Summary
Severity: Unknown
Chain: Compound
Component: compound-finance/comet
Published: 2022-07-01
Source: https://github.com/compound-finance/comet/commit/bf20ccfa991578de670fcb5d6f3ae2362ebc6aa0
Type: security-commit

## Details
Fix overflow bug that occasionally occurs when supplying 0 base (#455)

This PR fixes a math overflow bug that occasionally occurs when supplying 0 base. I also added a unit test to verify the fix, as well as another unit test to show a weird quirk that can occur when withdrawing 0 base. 

**Bug details:**
In `supplyBase`, we calculate `dstPrincipalNew` using `dstPrincipal` (old principal value before amount is supplied). The formula is:

`int104 dstPrincipalNew = principalValue(presentValue(dstPrincipal) + signed104(amount))`

When `amount=0`, the formula condenses to:

`dstPrincipalNew = principalValue(presentValue(dstPrincipal))`

Due to the fact that both `principalValue` and `presentValue` round down in favor of the protocol, we can actually end up with a value of `dstPrincipalNew < dstPrincipal`. 

This breaks our assumption in `repayAndSupplyAmount` that `newPrincipal >= oldPrincipal` MUST be true. In the old code, this would cause `supplyAmount` returned from `repayAndSupplyAmount` to be an extremely large number (`uint104(-1)` to be precise), which would later cause an overflow during an addition operation. The new code now explicitly checks this assumption and sets both `repayAmount` and `supplyAmount` to 0 if the assumption is violated. We apply a similar check in `withdrawAndBorrowAmount` as well.

## Patch
### contracts/Comet.sol
```diff
@@ -589,9 +589,11 @@ contract Comet is CometMainInterface {
 
     /**
      * @dev The change in principal broken into repay and supply amounts
-     * @dev Note: The assumption `newPrincipal >= oldPrincipal` MUST be true
      */
     function repayAndSupplyAmount(int104 oldPrincipal, int104 newPrincipal) internal pure returns (uint104, uint104) {
+        // If the new principal is less than the old principal, then no amount has been repaid or supplied
+        if (newPrincipal < oldPrincipal) return (0, 0);
+
         if (newPrincipal <= 0) {
             return (uint104(newPrincipal - oldPrincipal), 0);
         } else if (oldPrincipal >= 0) {
@@ -603,9 +605,11 @@ contract Comet is CometMainInterface {
 
     /**
      * @dev The change in principal broken into withdraw and borrow amounts
-     * @dev Note: The assumption `oldPrincipal >= newPrincipal` MUST be true
      */
     function withdrawAndBorrowAmount(int104 oldPrincipal, int104 newPrincipal) internal pure returns (uint104, uint104) {
+        // If the new principal is greater than the old principal, then no amount has been withdrawn or borrowed
+        if (newPrincipal > oldPrincipal) return (0, 0);
+
         if (newPrincipal >= 0) {
             return (uint104(oldPrincipal - newPrincipal), 0);
         } else if (oldPrincipal <= 0) {
```

### test/supply-test.ts
```diff
@@ -193,6 +193,45 @@ describe('supplyTo', function () {
     });
   });
 
+  // This is an edge-case that can occur when a user supplies 0 base.
+  // When `amount=0` in `supplyBase`, `dstPrincipalNew = principalValue(presentValue(dstPrincipal))`
+  // In some cases, `dstPrincipalNew` can actually be less than `dstPrincipal` due to the fact
+  // that the principal value and present value functions round down. This breaks our assumption
+  // in `repayAndSupplyAmount` that `newPrincipal >= oldPrincipal` MUST be true. In the old code,
+  // this would cause `supplyAmount` to be an extremely large number (uint104(-1)), which would
+  // later cause an overflow during an addition operation. The new code now explicitly checks
+  // this assumption and sets both `repayAmount` and `supplyAmount` to 0 if the assumption is
+  // violated.
+  it('supplies 0 and does not revert when dstPrincipalNew < dstPrincipal', async () => {
+    const protocol = await makeProtocol({ base: 'USDC' });
+    const { comet, tokens, users: [alice] } = protocol;
+    const { USDC } = tokens;
+
+    await comet.setBasePrincipal(alice.address, 99999992291226);
+    await setTotalsBasic(comet, {
+      totalSupplyBase: 699999944771920,
+      baseSupplyIndex: 1000000131467072,
+    });
+
+    const s0 = await wait(comet.connect(alice).supply(USDC.address, 0));
+
+    expect(s0.receipt['events'].length).to.be.equal(2);
+    expect(event(s0, 0)).to.be.deep.equal({
+      Transfer: {
+        from: alice.address,
+        to: comet.address,
+        amount: BigInt(0),
+      }
+    });
+    expect(event(s0, 1)).to.be.deep.equal({
+      Supply: {
+        from: alice.address,
+        dst: alice.address,
+        amount: BigInt(0),
+      }
+    });
+  });
+
   it('user supply is same as total supply', async () => {
     const protocol = await makeProtocol({ base: 'USDC' });
     const { comet, tokens, users: [bob] } = protocol;
```

### test/withdraw-test.ts
```diff
@@ -193,6 +193,46 @@ describe('withdrawTo', function () {
     expect(Number(s0.receipt.gasUsed)).to.be.lessThan(110000);
   });
 
+  // This demonstrates a weird quirk of the present value/principal value rounding down math.
+  it('withdraws 0 but Comet Transfer event amount is 1', async () => {
+    const protocol = await makeProtocol({ base: 'USDC' });
+    const { comet, tokens, users: [alice] } = protocol;
+    const { USDC } = tokens;
+
+    await comet.setBasePrincipal(alice.address, 99999992291226);
+    await setTotalsBasic(comet, {
+      totalSupplyBase: 699999944771920,
+      baseSupplyIndex: 1000000131467072,
+    });
+
+    const s0 = await wait(comet.connect(alice).withdraw(USDC.address, 0));
+
+    expect(s0.receipt['events'].length).to.be.equal(3);
+    expect(event(s0, 0)).to.be.deep.equal({
+      Transfer: {
+        from: comet.address,
+        to: alice.address,
+        amount: 0n,
+      }
+    });
+    expect(event(s0, 1)).to.be.deep.equal({
+      Withdraw: {
+        src: alice.address,
+        to: alice.address,
+        amount: 0n,
+      }
+    });
+    // Weird quirk of round down behavior where `withdrawAmount` is 1 even though
+    // `amount` is 0. So no base leaves Comet (which is expected)
+    expect(event(s0, 2)).to.be.deep.equal({
+      Transfer: {
+        from: alice.address,
+        to: ethers.constants.AddressZero,
+        amount: 1n,
+      }
+    });
+  });
+
   it('withdraws collateral from sender if the asset is collateral', async () => {
     const protocol = await makeProtocol();
     const { comet, tokens, users: [alice, bob] } = protocol;
```
