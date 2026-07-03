Audit Report

## Title
Deposits Mint rsETH Using Stale Cached `rsETHPrice` Without Prior Oracle Update, Enabling Yield Extraction From Existing Holders - (File: contracts/LRTDepositPool.sol)

## Summary
`LRTDepositPool.depositETH` and `depositAsset` compute the rsETH mint amount via `getRsETHAmountToMint`, which divides by `lrtOracle.rsETHPrice()` — a stored state variable in `LRTOracle` that is only updated when `_updateRsETHPrice()` is explicitly invoked. Neither deposit function nor `_beforeDeposit` triggers a price update before the calculation, so any accrued staking rewards that have increased the protocol's TVL since the last update cause depositors to receive excess rsETH, diluting the yield owed to existing holders.

## Finding Description
`getRsETHAmountToMint` at `LRTDepositPool.sol:520` computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` is a live external call, but `lrtOracle.rsETHPrice()` reads the stored state variable declared at `LRTOracle.sol:28`:

```solidity
uint256 public override rsETHPrice;
```

This variable is only written at `LRTOracle.sol:313` inside `_updateRsETHPrice()`. The public entry point `updateRSETHPrice()` at `LRTOracle.sol:87` is `public whenNotPaused` with no automatic invocation from the deposit path.

`_beforeDeposit` (`LRTDepositPool.sol:648–670`) is declared `private view`, making it structurally incapable of updating state. `depositETH` (`LRTDepositPool.sol:76–93`) calls `_beforeDeposit` directly without any preceding price update. The same applies to `depositAsset`.

When staking rewards increase `totalETHInProtocol` between oracle updates, `rsETHPrice` understates the true per-share value. A depositor mints `amount / P_stale` rsETH instead of the correct `amount / P_actual`, where `P_stale < P_actual`. The excess rsETH represents a larger ownership fraction than the deposit warrants.

The `pricePercentageLimit` guard at `LRTOracle.sol:252–266` compounds the issue: if the true price has risen beyond the configured threshold, the public `updateRSETHPrice()` reverts for non-managers with `PriceAboveDailyThreshold`, meaning the stale price can persist for an extended period while deposits continue at the outdated rate.

## Impact Explanation
This is **theft of unclaimed yield** (High severity). After `updateRSETHPrice()` is eventually called, the attacker's rsETH — minted at the stale price — is worth more than the deposited amount. The surplus value is extracted from the yield that had accrued to pre-existing holders, whose proportional share of the protocol is permanently diluted. The impact is concrete and bounded by the magnitude of accrued rewards and deposit size.

## Likelihood Explanation
`updateRSETHPrice()` is callable by any unprivileged address. EigenLayer restaking rewards accrue continuously, so a staleness window exists after every reward accrual event. The attacker requires no privileged access: monitor on-chain `rsETHPrice` vs. computed TVL, deposit at the stale price, then call `updateRSETHPrice()` (or wait for the manager). The attack is repeatable every reward cycle. The `pricePercentageLimit` mechanism can extend the exploitable window by blocking the public price update, making the attack more profitable.

## Recommendation
Call `_updateRsETHPrice()` (or an internal equivalent) at the start of `_beforeDeposit` before computing `rsethAmountToMint`. This requires changing `_beforeDeposit` from `private view` to `private` and adding the oracle update call:

```solidity
function _beforeDeposit(
    address asset,
    uint256 depositAmount,
    uint256 minRSETHAmountExpected
) private returns (uint256 rsethAmountToMint) {
    ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();

    if (depositAmount == 0 || depositAmount < minAmountToDeposit) revert InvalidAmountToDeposit();
    if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) revert MaximumDepositLimitReached();

    rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
    if (rsethAmountToMint < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
}
```

## Proof of Concept
1. At `t=0`: `rsETHPrice = 1.00 ETH`, total ETH in protocol = 1000 ETH, rsETH supply = 1000.
2. At `t=1`: Staking rewards add 10 ETH. True price = 1010/1000 = 1.01 ETH. `rsETHPrice` remains `1.00`.
3. Attacker calls `depositETH{value: 100 ETH}`:
   - `rsethAmountToMint = 100 / 1.00 = 100 rsETH` (correct would be `100 / 1.01 ≈ 99.01 rsETH`).
4. Attacker calls `updateRSETHPrice()`:
   - New supply = 1100 rsETH, new TVL = 1110 ETH.
   - `rsETHPrice = 1110 / 1100 ≈ 1.009 ETH`.
5. Attacker holds 100 rsETH worth `100 × 1.009 = 100.9 ETH` — deposited 100 ETH, extracted ~0.9 ETH of yield from existing holders.

**Foundry fork test outline:**
- Fork mainnet, set `rsETHPrice = 1e18`, simulate reward accrual by directly increasing `totalETHInProtocol`.
- Call `depositETH` as attacker, record rsETH minted.
- Call `updateRSETHPrice()`, record new `rsETHPrice`.
- Assert attacker's rsETH value > deposited ETH, and existing holder's rsETH value < pre-deposit value.