Audit Report

## Title
L2 Oracle Rate Lag Causes wrsETH Over-Minting and Structural Wrapper Undercollateralization - (File: contracts/pools/RSETHPoolV3.sol, contracts/L1Vault.sol)

## Summary
`RSETHPoolV3.deposit()` mints wrsETH to users immediately using the L2 oracle rate stored in `RSETHRateReceiver`, which is updated asynchronously via LayerZero from L1. The deposited ETH is later converted to rsETH on L1 at the then-current `LRTOracle.rsETHPrice()`. Because rsETH price increases monotonically and the L2 oracle always lags behind, every deposit during the lag window mints more wrsETH than the rsETH that will back it, permanently undercollateralizing the `RsETHTokenWrapper`.

## Finding Description

**L2 oracle is a stale cross-chain snapshot.** `RSETHRateReceiver` stores the rate pushed from `RSETHMultiChainRateProvider` on L1 via LayerZero. The provider reads `ILRTOracle(rsETHPriceOracle).rsETHPrice()` at the time of the push and encodes it in a message. The receiver stores it only when the message arrives:

```solidity
// CrossChainRateReceiver.sol L93-97
uint256 _rate = abi.decode(_payload, (uint256));
rate = _rate;
lastUpdated = block.timestamp;
```

Between pushes, `rate` is frozen while the L1 price continues to rise.

**Step 1 — L2 deposit mints wrsETH at stale rate.** `RSETHPoolV3.deposit()` calls `viewSwapRsETHAmountAndFee`, which divides by `getRate()` (the stale L2 oracle value), then immediately mints wrsETH:

```solidity
// RSETHPoolV3.sol L258-262
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);
```

```solidity
// RSETHPoolV3.sol L304-307
uint256 rsETHToETHrate = getRate();          // stale L2 rate
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**Step 2 — L1 deposit mints rsETH at current rate.** The bridger moves ETH to L1; the manager calls `depositETHForL1VaultETH()`, which uses the live `lrtOracle.rsETHPrice()`:

```solidity
// L1Vault.sol L151-158
uint256 balanceOfETH = address(this).balance;
uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);
lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");
```

```solidity
// LRTDepositPool.sol L519-520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**The shortfall is permanent.** `RsETHTokenWrapper._withdraw()` burns wrsETH and transfers rsETH 1:1. `maxAmountToDepositBridgerAsset()` enforces that the bridger can only deposit up to `wrsETHSupply - rsETHBalance`, so the deficit cannot be papered over by depositing extra rsETH. The wrapper is structurally short by exactly `wrsETHMinted - rsETHReceived` for every deposit made while the oracle lags.

No existing guard prevents deposits when the L2 oracle is stale. The daily mint limit caps total volume but does not close the rate gap. The `paused` flag requires privileged action and is not triggered automatically on oracle staleness.

## Impact Explanation

**Critical — Protocol insolvency.** The `RsETHTokenWrapper` promises 1:1 redemption of wrsETH for rsETH. Every deposit during an oracle lag window creates a permanent rsETH shortfall in the wrapper. The deficit compounds with each deposit and is absorbed by existing wrsETH holders, who cannot redeem their full rsETH entitlement. This is direct, irreversible loss of user funds matching the "Protocol insolvency" critical impact class.

## Likelihood Explanation

**Medium.** The L2 oracle lag is a structural property of the system, not an edge case. rsETH price increases continuously as EigenLayer staking rewards accrue. The cross-chain push is periodic and permissionless but not atomic with L1 price updates. The additional bridging delay (L2→L1 ETH transit) and the manager's manual call to `depositETHForL1VaultETH()` further widen the window between wrsETH minting and rsETH backing. No special attacker capability is required — any depositor benefits from the stale rate passively. The divergence is small per block but material over hours or days of oracle lag, and it is repeatable across all L2 deployments.

## Recommendation

1. **Mint wrsETH only after rsETH is confirmed.** Issue a non-transferable receipt at deposit time and mint wrsETH only after the bridged rsETH arrives in the wrapper, using the actual rsETH amount received as the mint amount.
2. **Alternatively, record the L2 rate at deposit time** and pass it as a minimum rsETH expectation to the L1 deposit step, reverting if the L1 execution yields fewer rsETH than the wrsETH already minted.
3. **Enforce a maximum oracle staleness check** in `deposit()`: revert if `block.timestamp - RSETHRateReceiver.lastUpdated` exceeds a threshold (e.g., 1 hour), preventing deposits when the L2 rate is known to be stale.

## Proof of Concept

**Preconditions:**
- L1 `rsETHPrice` = 1.05e18 (current, reflects latest staking rewards)
- L2 `RSETHRateReceiver.rate` = 1.03e18 (last pushed 6 hours ago, stale)

**Step 1 — Attacker deposits 100 ETH on L2:**
```
rsETHAmount = 100e18 * 1e18 / 1.03e18 ≈ 97.087e18 wrsETH minted to attacker
```

**Step 2 — Bridger moves 100 ETH to L1; manager calls `depositETHForL1VaultETH()`:**
```
rsethAmountToMint = 100e18 * 1e18 / 1.05e18 ≈ 95.238e18 rsETH minted on L1
```

**Step 3 — rsETH bridged back to wrapper:**
- wrsETH in circulation from this deposit: **97.087**
- rsETH deposited into wrapper to back it: **95.238**
- **Permanent shortfall: ~1.849 rsETH** (~1.85% of deposit value)

**Foundry fork test plan:**
1. Fork mainnet; deploy `RSETHRateReceiver` with a rate 2% below current `LRTOracle.rsETHPrice()`.
2. Call `RSETHPoolV3.deposit{value: 100 ether}("")`.
3. Assert `wrsETH.balanceOf(attacker) > rsETH_that_will_be_minted_on_L1`.
4. Simulate the full bridge cycle; call `L1Vault.depositETHForL1VaultETH()`.
5. Bridge rsETH back; call `RsETHTokenWrapper.depositBridgerAssets()`.
6. Assert `wrsETH.totalSupply() > rsETH.balanceOf(address(wrapper))` — wrapper is undercollateralized.
7. Assert attacker cannot fully redeem their wrsETH for rsETH without depleting other holders' backing.