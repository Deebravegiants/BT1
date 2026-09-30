# [?] more tests, fix the overflow behavior (#306)

## Summary
Severity: Unknown
Chain: Uniswap
Component: Uniswap/v3-core
Published: 2021-01-20
Source: https://github.com/Uniswap/v3-core/commit/baa1f72548c4bdf3d5279810056b42ef77607494
Type: security-commit

## Details
more tests, fix the overflow behavior (#306)

* add some scry tests

* more tests, use snapshots

* more tests, a fix

* snapshots, move test out

* load fixture

* load fixture

* fix tests

* some gas tests for scry, some reorganization

* check now external again

* fix the check

* just make it private again + failing test

* another fix

## Patch
### contracts/libraries/Oracle.sol
```diff
@@ -97,10 +97,10 @@ library Oracle {
         uint16 cardinality
     ) private view returns (Observation memory before, Observation memory atOrAfter) {
         uint16 l = (index + 1) % cardinality; // oldest observation
-        uint16 r = l + cardinality - 1; // newest observation
+        uint16 r = index; // newest observation
         uint16 i;
         while (true) {
-            i = (l + r) / 2;
+            i = ((r - l) % cardinality) / 2 + l;
 
             atOrAfter = self[i % cardinality];
 
@@ -136,7 +136,7 @@ library Oracle {
     // fetches the observations before and atOrAfter a target, i.e. where this range is satisfied: (before, atOrAfter]
     function getSurroundingObservations(
         Observation[65535] storage self,
-        uint32 current,
+        uint32 time,
         uint32 target,
         int24 tick,
         uint16 index,
@@ -151,11 +151,8 @@ library Oracle {
             assert(beforeOrAt.initialized);
         }
 
-        // ensure that the target is greater than the oldest observation (accounting for wrapping)
-        require(
-            beforeOrAt.blockTimestamp <= target || (beforeOrAt.blockTimestamp > current && target <= current),
-            'OLD'
-        );
+        // ensure that the target is greater than the oldest observation (accounting for block timestamp overflow)
+        require(beforeOrAt.blockTimestamp <= target && (target <= time || beforeOrAt.blockTimestamp >= time), 'OLD');
 
         // now, optimistically set before to the newest observation
         beforeOrAt = self[index];
@@ -167,11 +164,11 @@ library Oracle {
         // adjust for overflow
         uint256 beforeAdjusted = beforeOrAt.blockTimestamp;
         uint256 targetAdjusted = target;
-        if (beforeAdjusted > current && targetAdjusted <= current) targetAdjusted += 2**32;
-        if (targetAdjusted > current) beforeAdjusted += 2**32;
+        if (beforeAdjusted > time && targetAdjusted <= time) targetAdjusted += 2**32;
+        if (targetAdjusted > time) beforeAdjusted += 2**32;
 
         // once here, check if we're right and return a counterfactual observation for atOrAfter
-        if (beforeAdjusted < targetAdjusted) return (beforeOrAt, transform(beforeOrAt, current, tick, liquidity));
+        if (beforeAdjusted < targetAdjusted) return (beforeOrAt, transform(beforeOrAt, time, tick, liquidity));
 
         // we're wrong, so perform binary search
         return binarySearch(self, target, index, cardinality);
```

### contracts/test/OracleEchidnaTest.sol
```diff
@@ -47,12 +47,13 @@ contract OracleEchidnaTest {
         oracle.grow(target);
     }
 
-    // private for now since it causes the test to run for too long
     function checkTimeWeightedResultAssertions(uint32 secondsAgo0, uint32 secondsAgo1) private view {
         require(secondsAgo0 != secondsAgo1);
-        if (secondsAgo0 > secondsAgo1) (secondsAgo0, secondsAgo1) = (secondsAgo1, secondsAgo0);
+        require(initialized);
+        // secondsAgo0 should be the larger one
+        if (secondsAgo0 < secondsAgo1) (secondsAgo0, secondsAgo1) = (secondsAgo1, secondsAgo0);
 
-        uint32 timeElapsed = secondsAgo1 - secondsAgo0;
+        uint32 timeElapsed = secondsAgo0 - secondsAgo1;
 
         (int56 tickCumulative0, uint160 liquidityCumulative0) = oracle.scry(secondsAgo0);
         (int56 tickCumulative1, uint160 liquidityCumulative1) = oracle.scry(secondsAgo1);
```

### test/Oracle.spec.ts
```diff
@@ -1,7 +1,9 @@
+import { BigNumberish } from 'ethers'
 import { ethers, waffle } from 'hardhat'
 import { OracleTest } from '../typechain/OracleTest'
 import checkObservationEquals from './shared/checkObservationEquals'
 import { expect } from './shared/expect'
+import { TEST_PAIR_START_TIME } from './shared/fixtures'
 import snapshotGasCost from './shared/snapshotGasCost'
 
 describe('Oracle', () => {
@@ -257,149 +259,239 @@ describe('Oracle', () => {
   })
 
   describe('#scry', () => {
-    let oracle: OracleTest
-    beforeEach('deploy test oracle', async () => {
-      oracle = await loadFixture(oracleFixture)
-    })
+    describe('before initialization', async () => {
+      let oracle: OracleTest
+      beforeEach('deploy test oracle', async () => {
+        oracle = await loadFixture(oracleFixture)
+      })
 
-    it('fails before initialize', async () => {
-      await expect(oracle.scry(0)).to.be.revertedWith('')
-    })
+      it('fails before initialize', async () => {
+        await expect(oracle.scry(0)).to.be.revertedWith('')
+      })
 
-    it('fails if an older observation does not exist', async () => {
-      await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
-      await expect(oracle.scry(1)).to.be.revertedWith('OLD')
-    })
+      it('fails if an older observation does not exist', async () => {
+        await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
+        await expect(oracle.scry(1)).to.be.revertedWith('OLD')
+      })
 
-    it('single observation at current time', async () => {
-      await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
-      expect(tickCumulative).to.eq(0)
-      expect(liquidityCumulative).to.eq(0)
-    })
+      it('single observation at current time', async () => {
+        await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+        expect(tickCumulative).to.eq(0)
+        expect(liquidityCumulative).to.eq(0)
+      })
 
-    it('single observation in past but not earlier than secondsAgo', async () => {
-      await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
-      await oracle.advanceTime(3)
-      await expect(oracle.scry(4)).to.be.revertedWith('OLD')
-    })
+      it('single observation in past but not earlier than secondsAgo', async () => {
+        await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
+        await oracle.advanceTime(3)
+        await expect(oracle.scry(4)).to.be.revertedWith('OLD')
+      })
 
-    it('single observation in past at exactly seconds ago', async () => {
-      await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
-      await oracle.advanceTime(3)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(3)
-      expect(tickCumulative).to.eq(0)
-      expect(liquidityCumulative).to.eq(0)
-    })
+      it('single observation in past at exactly seconds ago', async () => {
+        await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
+        await oracle.advanceTime(3)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(3)
+        expect(tickCumulative).to.eq(0)
+        expect(liquidityCumulative).to.eq(0)
+      })
 
-    it('single observation in past counterfactual in past', async () => {
-      await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
-      await oracle.advanceTime(3)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(1)
-      expect(tickCumulative).to.eq(4)
-      expect(liquidityCumulative).to.eq(8)
-    })
+      it('single observation in past counterfactual in past', async () => {
+        await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
+        await oracle.advanceTime(3)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(1)
+        expect(tickCumulative).to.eq(4)
+        expect(liquidityCumulative).to.eq(8)
+      })
 
-    it('single observation in past counterfactual now', async () => {
-      await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
-      await oracle.advanceTime(3)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
-      expect(tickCumulative).to.eq(6)
-      expect(liquidityCumulative).to.eq(12)
-    })
+      it('single observation in past counterfactual now', async () => {
+        await oracle.initialize({ liquidity: 4, tick: 2, time: 5 })
+        await oracle.advanceTime(3)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+        expect(tickCumulative).to.eq(6)
+        expect(liquidityCumulative).to.eq(12)
+      })
 
-    it('two observations in chronological order 0 seconds ago exact', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
-      expect(tickCumulative).to.eq(-20)
-      expect(liquidityCumulative).to.eq(20)
-    })
+      it('two observations in chronological order 0 seconds ago exact', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+        expect(tickCumulative).to.eq(-20)
+        expect(liquidityCumulative).to.eq(20)
+      })
 
-    it('two observations in chronological order 0 seconds ago counterfactual', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      await oracle.advanceTime(7)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
-      expect(tickCumulative).to.eq(-13)
-      expect(liquidityCumulative).to.eq(34)
-    })
+      it('two observations in chronological order 0 seconds ago counterfactual', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        await oracle.advanceTime(7)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+        expect(tickCumulative).to.eq(-13)
+        expect(liquidityCumulative).to.eq(34)
+      })
 
-    it('two observations in chronological order seconds ago is exactly on first observation', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      await oracle.advanceTime(7)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(11)
-      expect(tickCumulative).to.eq(0)
-      expect(liquidityCumulative).to.eq(0)
-    })
+      it('two observations in chronological order seconds ago is exactly on first observation', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        await oracle.advanceTime(7)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(11)
+        expect(tickCumulative).to.eq(0)
+        expect(liquidityCumulative).to.eq(0)
+      })
 
-    it('two observations in chronological order seconds ago is between first and second', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      await oracle.advanceTime(7)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(9)
-      expect(tickCumulative).to.eq(-10)
-      expect(liquidityCumulative).to.eq(10)
-    })
+      it('two observations in chronological order seconds ago is between first and second', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        await oracle.advanceTime(7)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(9)
+        expect(tickCumulative).to.eq(-10)
+        expect(liquidityCumulative).to.eq(10)
+      })
 
-    it('two observations in reverse order 0 seconds ago exact', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
-      expect(tickCumulative).to.eq(-17)
-      expect(liquidityCumulative).to.eq(26)
-    })
+      it('two observations in reverse order 0 seconds ago exact', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+        expect(tickCumulative).to.eq(-17)
+        expect(liquidityCumulative).to.eq(26)
+      })
 
-    it('two observations in reverse order 0 seconds ago counterfactual', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
-      await oracle.advanceTime(7)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
-      expect(tickCumulative).to.eq(-52)
-      expect(liquidityCumulative).to.eq(54)
-    })
+      it('two observations in reverse order 0 seconds ago counterfactual', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
+        await oracle.advanceTime(7)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+        expect(tickCumulative).to.eq(-52)
+        expect(liquidityCumulative).to.eq(54)
+      })
 
-    it('two observations in reverse order seconds ago is exactly on first observation', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
-      await oracle.advanceTime(7)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(10)
-      expect(tickCumulative).to.eq(-20)
-      expect(liquidityCumulative).to.eq(20)
-    })
+      it('two observations in reverse order seconds ago is exactly on first observation', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
+        await oracle.advanceTime(7)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(10)
+        expect(tickCumulative).to.eq(-20)
+        expect(liquidityCumulative).to.eq(20)
+      })
 
-    it('two observations in reverse order seconds ago is between first and second', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.grow(2)
-      await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
-      await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
-      await oracle.advanceTime(7)
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(9)
-      expect(tickCumulative).to.eq(-19)
-      expect(liquidityCumulative).to.eq(22)
-    })
+      it('two observations in reverse order seconds ago is between first and second', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.grow(2)
+        await oracle.update({ advanceTimeBy: 4, tick: 1, liquidity: 2 })
+        await oracle.update({ advanceTimeBy: 3, tick: -5, liquidity: 4 })
+        await oracle.advanceTime(7)
+        const { tickCumulative, liquidityCumulative } = await oracle.scry(9)
+        expect(tickCumulative).to.eq(-19)
+        expect(liquidityCumulative).to.eq(22)
+      })
 
-    it('gas for single observation at current time', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await snapshotGasCost(oracle.getGasCostOfScry(0))
-    })
+      it('gas for single observation at current time', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await snapshotGasCost(oracle.getGasCostOfScry(0))
+      })
 
-    it('gas for single observation at current time counterfactually computed', async () => {
-      await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
-      await oracle.advanceTime(5)
-      await snapshotGasCost(oracle.getGasCostOfScry(0))
+      it('gas for single observation at current time counterfactually computed', async () => {
+        await oracle.initialize({ liquidity: 5, tick: -5, time: 5 })
+        await oracle.advanceTime(5)
+        await snapshotGasCost(oracle.getGasCostOfScry(0))
+      })
     })
+
+    for (let startingTime of [5, 2 ** 32 - 5]) {
+      describe(`initialized with 5 observations with starting time of ${startingTime}`, () => {
+        const oracleFixture5Observations = async () => {
+          const oracle = await oracleFixture()
+          await oracle.initialize({ liquidity: 5, tick: -5, time: startingTime })
+          await oracle.grow(5)
+          await oracle.update({ advanceTimeBy: 3, tick: 1, liquidity: 2 })
+          await oracle.update({ advanceTimeBy: 2, tick: -6, liquidity: 4 })
+          await oracle.update({ advanceTimeBy: 4, tick: -2, liquidity: 4 })
+          await oracle.update({ advanceTimeBy: 1, tick: -2, liquidity: 9 })
+          await oracle.update({ advanceTimeBy: 3, tick: 4, liquidity: 2 })
+          await oracle.update({ advanceTimeBy: 6, tick: 6, liquidity: 7 })
+          return oracle
+        }
+        let oracle: OracleTest
+        beforeEach('set up observations', async () => {
+          oracle = await loadFixture(oracleFixture5Observations)
+        })
+
+        it('index, cardinality, target', async () => {
+          expect(await oracle.index()).to.eq(1)
+          expect(await oracle.cardinality()).to.eq(5)
+          expect(await oracle.target()).to.eq(5)
+        })
+        it('latest observation same time as latest', async () => {
+          const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+          expect(tickCumulative).to.eq(-21)
+          expect(liquidityCumulative).to.eq(78)
+        })
+        it('latest observation 5 seconds after latest', async () => {
+          await oracle.advanceTime(5)
+          const { tickCumulative, liquidityCumulative } = await oracle.scry(5)
+          expect(tickCumulative).to.eq(-21)
+          expect(liquidityCumulative).to.eq(78)
+        })
+        it('current observation 5 seconds after latest', async () => {
+          await oracle.advanceTime(5)
+          const { tickCumulative, liquidityCumulative } = await oracle.scry(0)
+          expect(tickCumulative).to.eq(9)
+          expect(liquidityCumulative).to.eq(113)
+        })
+        it('between latest observation and just before latest observation at same time as latest', async () => {
+          const { tickCumulative, liquidityCumulative } = await oracle.scry(3)
+          expect(tickCumulative).to.eq(-33)
+          expect(liquidityCumulative).to.eq(72)
+        })
+        it('between latest observation and just before latest observation after the latest observation', async () => {
+          await oracle.advanceTime(5)
+          const { tickCumulative, liquidityCumulative } = await oracle.scry(8)
+          expect(tickCumulative).to.eq(-33)
+          expect(liquidityCumulative).to.eq(72)
+        })
+        it('older than oldest reverts', async () => {
+          await expect(oracle.scry(15)).to.be.revertedWith('OLD')
+          await oracle.advanceTime(5)
+          await expect(oracle.scry(20)).to.be.revertedWith('OLD')
+        })
+        it('oldest observation', async () => {
+          const { tickCumulative, liquidityCumulative } = await oracle.scry(14)
+          expect(tickCumulative).to.eq(-13)
+          expect(liquidityCumulative).to.eq(19)
+        })
+        it('oldest observation after some time', async () => {
+          await oracle.advanceTime(6)
+          const { tickCumulative, liquidityCumulative } = await oracle.scry(20)
+          expect(tickCumulative).to.eq(-13)
+          expect(liquidityCumulative).to.eq(19)
+        })
+
+        it('gas latest equal', async () => {
+          await snapshotGasCost(oracle.getGasCostOfScry(0))
+        })
+        it('gas latest transform', async () => {
+          await oracle.advanceTime(5)
+          await snapshotGasCost(oracle.getGasCostOfScry(0))
+        })
+        it('gas oldest', async () => {
+          await snapshotGasCost(oracle.getGasCostOfScry(14))
+        })
+        it('gas between oldest and oldest + 1', async () => {
+          await snapshotGasCost(oracle.getGasCostOfScry(13))
+        })
+        it('gas middle', async () => {
+          await snapshotGasCost(oracle.getGasCostOfScry(5))
+        })
+      })
+    }
   })
 
   describe.skip('full oracle', function () {
@@ -409,9 +501,11 @@ describe('Oracle', () => {
 
     const BATCH_SIZE = 300
 
+    const STARTING_TIME = TEST_PAIR_START_TIME
+
     const maxedOutOracleFixture = async () => {
       const oracle = await oracleFixture()
-      await oracle.initialize({ liquidity: 0, tick: 0, time: 1 })
+      await oracle.initialize({ liquidity: 0, tick: 0, time: STARTING_TIME })
       let cardinality = await oracle.cardinality()
       while (cardinality < 65535) {
         const cardinalityNext = Math.min(65535, cardinality + BATCH_SIZE)
@@ -447,10 +541,93 @@ describe('Oracle', () => {
       expect(await oracle.cardinality()).to.eq(65535)
     })
 
-    it('can scry 13*65534 seconds ago', async () => {
-      const { tickCumulative, liquidityCumulative } = await oracle.scry(13 * 65534)
-      expect(tickCumulative).to.eq(5)
-      expect(liquidityCumulative).to.eq(15)
+    it('index wrapped around', async () => {
+      expect(await oracle.index()).to.eq(165)
+    })
+
+    async function checkScry(
+      secondsAgo: number,
+      expected?: { tickCumulative: BigNumberish; liquidityCumulative: BigNumberish }
+    ) {
+      const { tickCumulative, liquidityCumulative } = await oracle.scry(secondsAgo)
+      const check = {
+        tickCumulative: tickCumulative.toString(),
+        liquidityCumulative: liquidityCumulative.toString(),
+      }
+      if (typeof expected === 'undefined') {
+        expect(check).to.matchSnapshot()
+      } else {
+        expect(check).to.deep.eq({
+          tickCumulative: expected.tickCumulative.toString(),
+          liquidityCumulative: expected.liquidityCumulative.toString(),
+        })
+      }
+    }
+
+    it('can scry into the ordered portion with exact seconds ago', async () => {
+      await checkScry(100 * 13, {
+        liquidityCumulative: '27970560813',
+        tickCumulative: '-27970560813',
+      })
+    })
+
+    it('can scry into the ordered portion with unexact seconds ago', async () => {
+      await checkScry(100 * 13 + 5, {
+        liquidityCumulative: '27970232823',
+        tickCumulative: '-27970232823',
+      })
+    })
+
+    it('can scry at exactly the latest observation', async () => {
+      await checkScry(0, {
+        liquidityCumulative: '28055903863',
+        tickCumulative: '-28055903863',
+      })
+    })
+
+    it('can scry at exactly the latest observation after some time passes', async () => {
+      await oracle.advanceTime(5)
+      await checkScry(5, {
+        liquidityCumulative: '28055903863',
+        tickCumulative: '-28055903863',
+      })
+    })
+
+    it('can scry after the latest observation counterfactual', async () => {
+      await oracle.advanceTime(5)
+      await checkScry(3, {
+        liquidityCumulative: '28056035261',
+        tickCumulative: '-28056035261',
+      })
+    })
+
+    it('can scry into the unordered portion of array at exact seconds ago of observation', async () => {
+      await checkScry(200 * 13, {
+        liquidityCumulative: '27885347763',
+        tickCumulative: '-27885347763',
+      })
+    })
+
+    it('can scry into the unordered portion of array at seconds ago between observations', async () => {
+      await checkScry(200 * 13 + 5, {
+        liquidityCumulative: '27885020273',
+        tickCumulative: '-27885020273',
+      })
+    })
+
+    it('can scry the oldest observation 13*65534 seconds ago', async () => {
+      await checkScry(13 * 65534, {
+        liquidityCumulative: '175890',
+        tickCumulative: '-175890',
+      })
+    })
+
+    it('can scry the oldest observation 13*65534 + 5 seconds ago if time has elapsed', async () => {
+      await oracle.advanceTime(5)
+      await checkScry(13 * 65534 + 5, {
+        liquidityCumulative: '175890',
+        tickCumulative: '-175890',
+      })
     })
   })
 })
```

### test/__snapshots__/Oracle.spec.ts.snap
```diff
@@ -10,6 +10,26 @@ exports[`Oracle #grow gas for growing by 10 slots when index == cardinality - 1
 
 exports[`Oracle #initialize gas 1`] = `70116`;
 
-exports[`Oracle #scry gas for single observation at current time 1`] = `3825`;
+exports[`Oracle #scry before initialization gas for single observation at current time 1`] = `3870`;
 
-exports[`Oracle #scry gas for single observation at current time counterfactually computed 1`] = `4456`;
+exports[`Oracle #scry before initialization gas for single observation at current time counterfactually computed 1`] = `4501`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 5 gas between oldest and oldest + 1 1`] = `14716`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 5 gas latest equal 1`] = `3870`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 5 gas latest transform 1`] = `4501`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 5 gas middle 1`] = `14761`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 5 gas oldest 1`] = `7055`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 4294967291 gas between oldest and oldest + 1 1`] = `14716`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 4294967291 gas latest equal 1`] = `3870`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 4294967291 gas latest transform 1`] = `4501`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 4294967291 gas middle 1`] = `14761`;
+
+exports[`Oracle #scry initialized with 5 observations with starting time of 4294967291 gas oldest 1`] = `7055`;
```

### test/__snapshots__/UniswapV3Factory.spec.ts.snap
```diff
@@ -1,7 +1,7 @@
 // Jest Snapshot v1, https://goo.gl/fbAQLP
 
-exports[`UniswapV3Factory #createPair gas 1`] = `4383055`;
+exports[`UniswapV3Factory #createPair gas 1`] = `4387269`;
 
-exports[`UniswapV3Factory factory bytecode size 1`] = `24164`;
+exports[`UniswapV3Factory factory bytecode size 1`] = `24185`;
 
-exports[`UniswapV3Factory pair bytecode size 1`] = `21259`;
+exports[`UniswapV3Factory pair bytecode size 1`] = `21280`;
```
