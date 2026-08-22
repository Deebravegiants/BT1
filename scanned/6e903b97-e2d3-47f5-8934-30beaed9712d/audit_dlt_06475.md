# [M] `DataAssertionResolved(...)` event emitted even when assertion is not resolved truthfully

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-17
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/148
Type: hats-finding

## Details
**Github username:** @Audinarey
**Twitter username:** audinarey
**Submission hash (on-chain):** 0xf0461ebb0e0473ac2d99d95a66868907604b026be8789d7561d2515d88282699
**Severity:** medium

**Description:**
**Description**\
`OptimisticOracleIntegrator::assertionResolvedCallback(...)` is called by Optimistic Oracle V3 when an assertion is resolved. However, according to the [UMA docs](https://docs.uma.xyz/developers/optimistic-oracle-v3/data-asserter#resolving-and-subsequently-fetching-data-assertions), the `DataAssertionResolved(...)` event is supposed to be emmited ONLY when the assertion was resolved truthfully but the implementation of `OptimisticOracleIntegrator::assertionResolvedCallback(...)` emits this event whether or not the assertion was `true.

The problem is, that this inaccurate event logs can lead to misinterpretation of transaction outcomes, affecting audits, monitoring, and trust in the system's reporting accuracy for systems that rely on this event as a source of truth.


```solidity
File: OptimisticOracleIntegrator.sol
226:     function assertionResolvedCallback(
227:         bytes32 assertionId,
228:         bool assertedTruthfully
229:     ) public virtual {
230:         if (_msgSender() != address(oo)) {
231:             revert Module__OptimisticOracleIntegrator__CallerNotOO();
232:         }
233: 
234:         DataAssertion memory dataAssertion = assertionData[assertionId];
235: 
236: @>      emit DataAssertionResolved(
237:             assertedTruthfully,
238:             dataAssertion.dataId,
239:             dataAssertion.data,
240:             dataAssertion.asserter,
241:             assertionId
242:         );
243: 
244:         // If the assertion was true, then the data assertion is resolved.
245:         if (assertedTruthfully) {
246:             assertionData[assertionId].resolved = true;
247:         } else {
248:             delete assertionData[assertionId];
249:         } // Else delete the data assertion if it was false to save gas.
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/148_
