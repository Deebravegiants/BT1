### Title
`setPoolAdminFeeDestination` Rebinds Fee Recipient Without Settling Accrued Fees, Redirecting Already-Earned Admin Fees to New Destination - (File: `metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPoolFactory.setPoolAdminFeeDestination` overwrites `poolAdminFeeDestination[pool]` without first calling `collectFees` at the old destination. All spread-fee surplus and notional-fee accumulator balances that accrued under the old destination are silently redirected to the new one on the next `collectPoolFees` call.

---

### Finding Description

Every other fee-mutating path in `MetricOmmPoolFactory` follows a settle-then-change pattern. Both `setPoolAdminFees` and `setPoolProtocolFee` call `pool.collectFees(…, poolAdminFeeDestination[pool])` with the **old** destination before updating any state:

```solidity
// setPoolAdminFees — correct: settles first
IMetricOmmPoolCollectFees(pool).collectFees(
    c.protocolSpreadFeeE6, c.adminSpreadFeeE6,
    c.protocolNotionalFeeE8, c.adminNotionalFeeE8,
    poolAdminFeeDestination[pool]   // ← old destination receives accrued fees
);
c.adminSpreadFeeE6 = newAdminSpreadFeeE6;
```

`setPoolAdminFeeDestination` skips this step entirely:

```solidity
// setPoolAdminFeeDestination — missing settlement
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    poolAdminFeeDestination[pool] = newAdminFeeDestination;   // ← immediate overwrite
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
}
```

`collectFees` on the pool computes two independent fee pools at collection time:

1. **Spread surplus** — `balance * scaleMultiplier − binTotals.scaledToken0 − notionalFeeToken0Scaled`. This is real token balance sitting in the pool above LP-owned amounts, accumulated since the last collection.
2. **Notional accumulator** — `notionalFeeToken0Scaled` / `notionalFeeToken1Scaled`, incremented on every swap.

Both are sent to whichever address `adminFeeDestination_` is at the moment `collectFees` executes. Because `collectPoolFees` is **permissionless**, anyone can trigger it immediately after the destination change, flushing all pre-transition accrued fees to the new address.

The pool admin (`poolAdmin[pool]`) and the admin fee destination (`poolAdminFeeDestination[pool]`) are set independently at pool creation and can be entirely different entities. A pool admin can therefore redirect fees that were earned by a separate treasury contract without that treasury's consent.

---

### Impact Explanation

The old admin fee destination loses all spread-fee surplus and notional-fee accumulator balances that accrued before the destination change. These are real ERC-20 token balances held by the pool contract. The new destination receives fees it did not earn. The magnitude equals the full admin share of every swap fee collected since the last `collectPoolFees` call.

---

### Likelihood Explanation

The trigger is a single pool admin transaction with no timelock. The pool admin role is not the fully-trusted factory owner; it is a per-pool role that can be a multisig, DAO, or any address set at deployment. The inconsistency with `setPoolAdminFees` (which does settle first) confirms the omission is unintentional and will be exercised whenever an admin legitimately rotates their treasury address without manually pre-collecting fees.

---

### Recommendation

Add a `collectFees` call at the old destination before overwriting `poolAdminFeeDestination[pool]`, mirroring the pattern used in `setPoolAdminFees` and `setPoolProtocolFee`:

```solidity
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    // Settle accrued fees at the OLD destination before rebinding
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool).collectFees(
        c.protocolSpreadFeeE6, c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8, c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
    );
    poolAdminFeeDestination[pool] = newAdminFeeDestination;
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
}
```

Add a regression test that verifies accrued fees are delivered to the old destination when `setPoolAdminFeeDestination` is called with a non-zero surplus and notional accumulator.

---

### Proof of Concept

1. Pool is deployed with `adminFeeDestination = treasuryA`, `adminSpreadFeeE6 > 0`, `adminNotionalFeeE8 > 0`.
2. Multiple swaps execute; `notionalFeeToken0Scaled` grows and a spread surplus accumulates above `binTotals.scaledToken0`.
3. Pool admin calls `setPoolAdminFeeDestination(pool, treasuryB)`. No fees are collected; `poolAdminFeeDestination[pool]` is immediately overwritten.
4. Any address calls `collectPoolFees(pool)`. The factory reads `poolAdminFeeDestination[pool] == treasuryB` and passes it to `collectFees`.
5. Inside `collectFees`, the full spread surplus and notional accumulator are split and transferred: the admin share goes to `treasuryB`.
6. `treasuryA` receives nothing despite having earned the fees during steps 1–2. `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` are zeroed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L212-220)
```text
    poolAdmin[pool] = params.admin;
    priceProviderTimelock[pool] = params.priceProviderTimelock;
    poolFeeConfig[pool] = PoolFeeConfig({
      protocolSpreadFeeE6: spreadProtocolFeeE6,
      adminSpreadFeeE6: params.adminSpreadFeeE6,
      protocolNotionalFeeE8: protocolNotionalFeeE8,
      adminNotionalFeeE8: params.adminNotionalFeeE8
    });
    poolAdminFeeDestination[pool] = params.adminFeeDestination;
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L379-389)
```text
  function collectPoolFees(address pool) external override nonReentrant {
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L417-425)
```text
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L438-447)
```text
  function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    poolAdminFeeDestination[pool] = newAdminFeeDestination;
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L382-433)
```text
    uint256 notionalFee0AmountScaled = notionalFeeToken0Scaled;
    uint256 notionalFee1AmountScaled = notionalFeeToken1Scaled;

    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;

    unchecked {
      uint256 spreadFee0ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * adminSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * adminSpreadFeeE6_) / spreadSumE6;

      uint256 spreadFee0ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * protocolSpreadFeeE6_) / spreadSumE6;

      uint256 notionalFee0ToAdminScaled =
        notionalSumE8 == 0 ? 0 : (notionalFee0AmountScaled * adminNotionalFeeE8_) / notionalSumE8;
      uint256 notionalFee1ToAdminScaled =
        notionalSumE8 == 0 ? 0 : (notionalFee1AmountScaled * adminNotionalFeeE8_) / notionalSumE8;

      uint256 notionalFee0ToProtocolScaled = notionalFee0AmountScaled - notionalFee0ToAdminScaled;
      uint256 notionalFee1ToProtocolScaled = notionalFee1AmountScaled - notionalFee1ToAdminScaled;

      uint256 totalFee0ToAdminScaled = spreadFee0ToAdminScaled + notionalFee0ToAdminScaled;
      uint256 totalFee1ToAdminScaled = spreadFee1ToAdminScaled + notionalFee1ToAdminScaled;

      uint256 totalFee0ToProtocolScaled = spreadFee0ToProtocolScaled + notionalFee0ToProtocolScaled;
      uint256 totalFee1ToProtocolScaled = spreadFee1ToProtocolScaled + notionalFee1ToProtocolScaled;

      (uint256 totalFee0ToAdmin, uint256 totalFee1ToAdmin) =
        deltasScaledToExternal(totalFee0ToAdminScaled, totalFee1ToAdminScaled, Math.Rounding.Floor);
      (uint256 totalFee0ToProtocol, uint256 totalFee1ToProtocol) =
        deltasScaledToExternal(totalFee0ToProtocolScaled, totalFee1ToProtocolScaled, Math.Rounding.Floor);

      if (totalFee0ToAdmin > 0) {
        transferToken0(adminFeeDestination_, totalFee0ToAdmin);
      }
      if (totalFee1ToAdmin > 0) {
        transferToken1(adminFeeDestination_, totalFee1ToAdmin);
      }
      if (totalFee0ToProtocol > 0) {
        transferToken0(FACTORY, totalFee0ToProtocol);
      }
      if (totalFee1ToProtocol > 0) {
        transferToken1(FACTORY, totalFee1ToProtocol);
      }

      notionalFeeToken0Scaled = 0;
      notionalFeeToken1Scaled = 0;

      emit ProtocolFeesCollected(totalFee0ToProtocol, totalFee1ToProtocol, totalFee0ToAdmin, totalFee1ToAdmin);
    }
```
