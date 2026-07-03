### Title
Protocol Fee Over-Minted When `updateRSETHPrice()` Is Called at a TVL Peak — (File: contracts/LRTOracle.sol)

### Summary

`LRTOracle.updateRSETHPrice()` is publicly callable by any address. It computes the protocol fee as a percentage of the **entire TVL increase since the last stored price snapshot**. Because the fee is calculated against a single point-in-time TVL reading rather than a time-weighted average, calling the function during a transient spike in underlying asset prices causes the protocol to permanently mint excess rsETH to the treasury — diluting all rsETH holders for a price movement that may fully reverse.

### Finding Description

`updateRSETHPrice()` is `public whenNotPaused`, meaning any unprivileged caller can trigger it at any time.

Inside `_updateRsETHPrice()`, the fee calculation is:

```solidity
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);   // last stored snapshot
...
uint256 rewardAmount = totalETHInProtocol - previousTVL; // entire increase since last call
protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
```

`totalETHInProtocol` is computed live from the current asset oracle prices at the moment of the call. `previousTVL` is anchored to the **last time** `updateRSETHPrice()` was called. If the function is not called for an extended period and the underlying asset prices are temporarily elevated when it is finally called, the entire TVL increase — including the transient portion — is treated as realised yield, and a fee is minted on it:

```solidity
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
```

This minted rsETH is permanent. When the asset prices revert to their prior level, the rsETH price drops, but the treasury retains the extra tokens — all other holders are permanently diluted.

The `pricePercentageLimit` guard only blocks price increases **above the configured threshold** for non-managers; spikes within the limit pass through unchecked. The `maxFeeMintAmountPerDay` cap limits per-day damage but does not prevent the structural mis-accounting.

### Impact Explanation

**High — Theft of unclaimed yield from rsETH holders.**

Every rsETH holder's share of the underlying ETH is reduced by the excess fee minted to the treasury. The dilution is permanent: even after asset prices normalise, the treasury's extra rsETH remains outstanding. The magnitude scales with (a) how long since the last price update and (b) how large the transient spike is.

### Likelihood Explanation

**Medium.** The function is not called automatically on every user interaction (unlike the perpetual asset case in the reference report). Any period of low activity — a weekend, a holiday, a bot outage — creates a window. Natural intra-day volatility in LST/LRT oracle prices (e.g., stETH/ETH rate fluctuations, EigenLayer restaking yield accrual events) can produce transient TVL spikes within the `pricePercentageLimit` band. No privileged access, oracle compromise, or flash-loan is required; a caller simply waits for a favourable moment and calls the public function.

### Recommendation

1. **Automate price updates**: Call `updateRSETHPrice()` on every deposit, withdrawal, and redemption so the snapshot gap is always minimal — analogous to the "regular settler worker" recommended in the reference report.
2. **Time-weight the fee base**: Accumulate yield continuously (e.g., per-block accrual) rather than computing it as a lump sum against a stale snapshot.
3. **Bound the snapshot gap**: Revert or skip fee minting if `block.timestamp - lastUpdated` exceeds a configurable maximum, forcing an operator to update before fees can be taken.

### Proof of Concept

1. Protocol is idle for 48 hours; `rsETHPrice` = 1.05 ETH, `totalKernelStaked` = 100 000 rsETH → `previousTVL` = 105 000 ETH.
2. A supported asset oracle temporarily reports a 2 % spike (within `pricePercentageLimit`); `totalETHInProtocol` = 107 100 ETH.
3. Attacker calls `updateRSETHPrice()`.
   - `rewardAmount` = 107 100 − 105 000 = 2 100 ETH (includes 2 100 ETH of transient spike).
   - At 10 % fee: `protocolFeeInETH` = 210 ETH.
   - `rsethAmountToMintAsProtocolFee` ≈ 210 / 1.071 ≈ 196 rsETH minted to treasury.
4. Asset price reverts; `totalETHInProtocol` drops back to 105 000 ETH.
5. New rsETH price = 105 000 / (100 000 + 196) ≈ 1.0479 ETH — all holders permanently diluted by ~0.2 % for a price movement that produced zero real yield.

Relevant lines: [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L233-247)
```text
        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L299-307)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```
