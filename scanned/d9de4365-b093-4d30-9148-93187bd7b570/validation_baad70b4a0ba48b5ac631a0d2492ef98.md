### Title
Blacklisted `adminFeeDestination` permanently blocks `collectFees()`, freezing protocol-fee collection and fee-parameter updates — (`metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPool.collectFees()` pushes tokens directly to `adminFeeDestination_` and `FACTORY` in a single atomic call. When the pool's token is USDC or USDT and `adminFeeDestination` is added to the token's blacklist, every call to `collectFees()` reverts. Because `MetricOmmPoolFactory.setPoolProtocolFee()` and `setPoolAdminFees()` both call `collectFees()` as a mandatory prerequisite, those factory-level fee-management operations are also permanently blocked for the affected pool.

---

### Finding Description

`MetricOmmPool.collectFees()` executes four sequential push-transfers:

```
transferToken0(adminFeeDestination_, totalFee0ToAdmin);   // line 417
transferToken1(adminFeeDestination_, totalFee1ToAdmin);   // line 420
transferToken0(FACTORY, totalFee0ToProtocol);             // line 423
transferToken1(FACTORY, totalFee1ToProtocol);             // line 425
``` [1](#0-0) 

`transferToken0` / `transferToken1` call `IERC20.safeTransfer`, which reverts on a blacklisted recipient. [2](#0-1) 

The notional-fee accounting reset (`notionalFeeToken0Scaled = 0`) happens **after** the transfers, so a revert leaves the accounting intact but makes the fees permanently uncollectable until the destination is changed. [3](#0-2) 

Three factory entry-points all call `collectFees()` before doing anything else:

1. `collectPoolFees()` — callable by anyone, reverts for the pool. [4](#0-3) 

2. `setPoolProtocolFee()` — factory owner cannot update the protocol fee for this pool. [5](#0-4) 

3. `setPoolAdminFees()` — pool admin cannot update their own fee split. [6](#0-5) 

The factory owner has no independent path to change `poolAdminFeeDestination`; only the pool admin can do so via `setPoolAdminFeeDestination()`. If the pool admin is unresponsive, the factory owner is permanently blocked from adjusting protocol fees on that pool. [7](#0-6) 

---

### Impact Explanation

- Accumulated protocol fees (spread surplus + notional fees) are locked inside the pool and cannot be swept to the factory or the admin destination.
- The factory owner loses the ability to update the protocol fee split for the affected pool, breaking a core governance operation.
- The pool admin loses the ability to update their own fee parameters until they separately call `setPoolAdminFeeDestination()` — but if the admin is the blacklisted party or is unresponsive, neither party can unblock the factory owner.

This constitutes a direct loss of owed protocol fees and broken core fee-management functionality, matching the "protocol fees" and "broken core pool functionality" impact gates.

---

### Likelihood Explanation

USDC and USDT both maintain on-chain blacklists used for sanctions compliance. The `adminFeeDestination` is a mutable address set at pool creation and changeable by the pool admin; it is commonly an EOA or a multisig, both of which are realistic blacklist targets. The pool does not validate that the destination is non-blacklistable. No special attacker capability is required — the blacklisting is an external event (e.g., OFAC sanctions) that can occur after pool deployment.

---

### Recommendation

Replace the push pattern in `collectFees()` with a pull (claim) pattern:

```solidity
mapping(address => mapping(address => uint256)) public claimable; // token => recipient => amount

// In collectFees(): accumulate instead of transfer
claimable[TOKEN0][adminFeeDestination_] += totalFee0ToAdmin;
claimable[TOKEN1][adminFeeDestination_] += totalFee1ToAdmin;
claimable[TOKEN0][FACTORY] += totalFee0ToProtocol;
claimable[TOKEN1][FACTORY] += totalFee1ToProtocol;

// Separate claimFees() function
function claimFees(address token, address recipient) external {
    uint256 amount = claimable[token][recipient];
    claimable[token][recipient] = 0;
    IERC20(token).safeTransfer(recipient, amount);
}
```

This decouples fee accounting from token delivery, so a blacklisted destination cannot block fee parameter updates or fee collection for other recipients.

---

### Proof of Concept

1. Deploy a USDC/USDT pool with `adminFeeDestination = Alice`.
2. Swaps occur; `notionalFeeToken0Scaled` and spread surplus accumulate.
3. USDC blacklists `Alice` (e.g., sanctions event).
4. Anyone calls `factory.collectPoolFees(pool)`:
   - `collectFees()` is entered.
   - `transferToken0(Alice, totalFee0ToAdmin)` → `USDC.safeTransfer(Alice, ...)` → reverts with `ERC20InvalidReceiver` or equivalent blacklist revert.
   - Entire transaction reverts; fees remain in pool.
5. Factory owner calls `factory.setPoolProtocolFee(pool, newFee, newNotional)`:
   - Same revert path; protocol fee cannot be updated.
6. Pool admin calls `factory.setPoolAdminFees(pool, newSpread, newNotional)`:
   - Same revert path; admin fee cannot be updated.
7. Factory owner has no function to override `poolAdminFeeDestination[pool]`; they are permanently blocked until the pool admin calls `setPoolAdminFeeDestination()`.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L416-427)
```text
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
```

**File:** metric-core/contracts/MetricOmmPool.sol (L429-430)
```text
      notionalFeeToken0Scaled = 0;
      notionalFeeToken1Scaled = 0;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L565-571)
```text
  function transferToken0(address to, uint256 amount) internal {
    IERC20(TOKEN0).safeTransfer(to, amount);
  }

  function transferToken1(address to, uint256 amount) internal {
    IERC20(TOKEN1).safeTransfer(to, amount);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L318-360)
```text
  function setPoolProtocolFee(address pool, uint24 newProtocolSpreadFeeE6, uint24 newProtocolNotionalFeeE8)
    external
    override
    onlyOwner
    nonReentrant
  {
    if (newProtocolSpreadFeeE6 > maxProtocolSpreadFeeE6) revert ProtocolFeeTooHigh();
    if (newProtocolNotionalFeeE8 > maxProtocolNotionalFeeE8) revert ProtocolFeeTooHigh();

    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );

    uint24 aSpread = c.adminSpreadFeeE6;
    uint24 aNotional = c.adminNotionalFeeE8;
    if (aSpread > maxAdminSpreadFeeE6) {
      aSpread = maxAdminSpreadFeeE6;
      emit PoolAdminSpreadFeeUpdated(pool, aSpread);
    }
    if (aNotional > maxAdminNotionalFeeE8) {
      aNotional = maxAdminNotionalFeeE8;
      emit PoolAdminNotionalFeeUpdated(pool, aNotional);
    }

    c = PoolFeeConfig({
      protocolSpreadFeeE6: newProtocolSpreadFeeE6,
      adminSpreadFeeE6: aSpread,
      protocolNotionalFeeE8: newProtocolNotionalFeeE8,
      adminNotionalFeeE8: aNotional
    });
    poolFeeConfig[pool] = c;

    IMetricOmmPoolFactoryActions(pool)
      .setPoolFees(c.protocolSpreadFeeE6 + c.adminSpreadFeeE6, c.protocolNotionalFeeE8 + c.adminNotionalFeeE8);
    emit PoolProtocolSpreadFeeUpdated(pool, newProtocolSpreadFeeE6);
    emit PoolProtocolNotionalFeeUpdated(pool, newProtocolNotionalFeeE8);
  }
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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L408-435)
```text
  function setPoolAdminFees(address pool, uint24 newAdminSpreadFeeE6, uint24 newAdminNotionalFeeE8)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();

    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );

    c.adminSpreadFeeE6 = newAdminSpreadFeeE6;
    c.adminNotionalFeeE8 = newAdminNotionalFeeE8;
    poolFeeConfig[pool] = c;

    IMetricOmmPoolFactoryActions(pool)
      .setPoolFees(c.protocolSpreadFeeE6 + c.adminSpreadFeeE6, c.protocolNotionalFeeE8 + c.adminNotionalFeeE8);
    emit PoolAdminSpreadFeeUpdated(pool, newAdminSpreadFeeE6);
    emit PoolAdminNotionalFeeUpdated(pool, newAdminNotionalFeeE8);
  }
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
