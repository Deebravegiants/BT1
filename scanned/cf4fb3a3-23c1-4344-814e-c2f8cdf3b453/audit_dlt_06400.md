# [M] Performance Fee calculation potential revenue loss on changing `performanceFee` value

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-02-27
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/40
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x27b35bb0f6f192d5811f998a737611b30b54681aba1bc735f803a6ee3f344554
**Severity:** medium

**Description:**
**Description**

The current performance fee calculation poses a risk of potential revenue loss. The calculation relies on the last recorded accumulated fee just before its collection. 

There is a `setPerformanceFee` for changing the performance fee value.

```js
File: OrigamiLovToken.sol
91:     function setPerformanceFee(uint256 _performanceFee) external override onlyElevatedAccess {
92:         if (_performanceFee > OrigamiMath.BASIS_POINTS_DIVISOR) revert CommonEventsAndErrors.InvalidParam();
93:         emit PerformanceFeeSet(_performanceFee);
94:         performanceFee = _performanceFee;
95:     }
```

The issue raised here is, during the performance fee frequency period, when there is a change in `performanceFee` value, then the old potential `performanceFee` amount will be omitted. If the change value is smaller, protocol will lose potential fee.

```js
File: OrigamiLovToken.sol
191:     function collectPerformanceFees() external override onlyElevatedAccess returns (uint256 amount) {
192:         if (block.timestamp < (lastPerformanceFeeTime + PERFORMANCE_FEE_FREQUENCY)) revert TooSoon();
193: 
194:         address _feeCollector = feeCollector;
195:         amount = performanceFeeAmount();
196:         if (amount != 0) {
197:             emit PerformanceFeesCollected(_feeCollector, amount);
198:             _mint(_feeCollector, amount);
199:         }
200: 
201:         lastPerformanceFeeTime = uint32(block.timestamp);
202:     }
...
387:     function performanceFeeAmount() public override view returns (uint256) {
388:         // totalSupply * feeBps * 7 days / 365 days / 10_000
389:         // Round down (protocol takes less of a fee)
390:         return OrigamiMath.mulDiv(
391:             totalSupply(), 
392: @>          performanceFee * PERFORMANCE_FEE_FREQUENCY, 
393:             OrigamiMath.BASIS_POINTS_DIVISOR * 365 days, 
394:             OrigamiMath.Rounding.ROUND_DOWN
395:         );
396:     }
```

For example, for simplicity (using percentage instead of bps).

Let's consider a scenario where the initial performance fee is set at 10% from day 1 to day 3. Subsequently, on day 4, the performanceFee is altered to 5%. Consequently, when collecting the performance fee, the protocol would receive an amount less than it should, as the calculation employs the last recorded value of 5%, overlooking the accumulated 10% fee over the initial three days.

**Attack Scenario**

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

**Recommendation**

Consider to use an accrual collection of fee and save into a temp unclaimed fee, thus when changing performanceFee it can to accrue first. 

Or if protocol want to keep this type of fee collection, maybe set a temporary pending `performanceFee` value, and apply the new change of performanceFee inside the `collectPerformanceFees` call.
