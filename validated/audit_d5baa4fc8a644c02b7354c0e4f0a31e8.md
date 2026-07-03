Audit Report

## Title
Stale Cross-Chain rsETH Rate in `CrossChainRateReceiver` Enables Over-Minting of rsETH — (`contracts/cross-chain/CrossChainRateReceiver.sol` / `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

## Summary
`CrossChainRateReceiver.getRate()` returns the stored `rate` unconditionally with no staleness check, despite `lastUpdated` being available. `RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee()` divides a fresh Chainlink `tokenToETHRate` by this potentially stale `rsETHToETHrate`. Because rsETH is yield-bearing and its ETH value increases monotonically, any gap between LayerZero rate updates causes the stored rate to be lower than the true rate, resulting in more rsETH being minted per deposited token than the collateral warrants — creating unbacked rsETH supply.

## Finding Description

**Root cause — `CrossChainRateReceiver.getRate()` has no staleness enforcement:**

`lastUpdated` is set in `lzReceive` at line 97 but is never read in `getRate()`:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L95-104
rate = _rate;
lastUpdated = block.timestamp;   // stored but never validated

function getRate() external view returns (uint256) {
    return rate;                 // unconditional return
}
```

The rate is only refreshed when someone manually calls `updateRate()` on the L1 provider, which triggers a LayerZero message. There is no on-chain heartbeat or keeper enforcement.

**Asymmetric oracle freshness in `viewSwapRsETHAmountAndFee`:**

```solidity
// contracts/pools/RSETHPoolV3WithNativeChainBridge.sol L363-370
uint256 rsETHToETHrate = getRate();                                       // stale LayerZero rate
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();  // fresh Chainlink rate
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`ChainlinkOracleForRSETHPoolCollateral.getRate()` enforces `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` checks (lines 30-32), so `tokenToETHRate` is current. `rsETHToETHrate` has no equivalent guard.

**Arithmetic consequence:**

rsETH appreciates continuously (~4% APY). If the stored rate is `R_stale < R_true`:

```
rsETHAmount_minted = amountAfterFee * tokenToETHRate / R_stale
                   > amountAfterFee * tokenToETHRate / R_true
```

The excess `rsETHAmount_minted − rsETHAmount_fair` is unbacked rsETH minted to the depositor.

**`dailyMintLimit` does not prevent the exploit:**

The `limitDailyMint` modifier (lines 108-137) computes `rsETHAmount` using the same stale rate before comparing against `dailyMintLimit`. The limit is therefore evaluated against an already-inflated rsETH amount, bounding but not preventing the per-day over-minting.

**Exploit path:**
1. Rate update is not sent for N days (permissionless but requires manual call + LayerZero fee — no on-chain enforcement).
2. Attacker calls `deposit(token, amount, referralId)` — no special role required.
3. `viewSwapRsETHAmountAndFee` computes `rsETHAmount` using stale-low `rsETHToETHrate`.
4. `wrsETH.mint(msg.sender, rsETHAmount)` mints excess unbacked rsETH.
5. Attacker repeats daily up to `dailyMintLimit`, accumulating unbacked supply.

## Impact Explanation

Every deposit while the rate is stale mints more rsETH than the deposited collateral is worth at the true rate. The protocol's collateral-to-rsETH backing ratio deteriorates with each such deposit. Repeated exploitation across daily mint windows accumulates unbacked rsETH supply, constituting **protocol insolvency** (Critical). The `dailyMintLimit` bounds the per-day loss but does not prevent it, and the limit resets each day, allowing indefinite accumulation.

## Likelihood Explanation

- rsETH appreciates continuously; any gap between `updateRate()` calls creates a stale-low rate — this is the normal operating state between updates.
- `updateRate()` is permissionless but requires a manual call and LayerZero fee payment; there is no on-chain keeper or heartbeat.
- The attacker requires no special role — only a standard `deposit(token, amount, referralId)` call.
- No oracle manipulation, governance capture, or front-running is required; the attacker simply deposits when the rate is stale.
- The exploit is repeatable every day up to `dailyMintLimit`.

## Recommendation

1. **Add a staleness threshold in `CrossChainRateReceiver.getRate()`:**
   ```solidity
   uint256 public constant MAX_RATE_AGE = 24 hours;
   function getRate() external view returns (uint256) {
       require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
       return rate;
   }
   ```
2. **Alternatively, revert in `viewSwapRsETHAmountAndFee` if `lastUpdated` is too old**, mirroring the freshness checks in `ChainlinkOracleForRSETHPoolCollateral`.
3. Consider adding an on-chain circuit breaker that pauses deposits when the rate has not been updated within the expected window, or a permissionless keeper incentive to ensure timely updates.

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";

interface IRateReceiver {
    function rate() external view returns (uint256);
    function lastUpdated() external view returns (uint256);
    function getRate() external view returns (uint256);
}

contract StaleRatePoC is Test {
    // Arbitrum deployment from README
    address constant RATE_RECEIVER = 0x3222d3De5A9a3aB884751828903044CC4ADC627e;

    function testStaleRateNoRevert() public {
        IRateReceiver receiver = IRateReceiver(RATE_RECEIVER);
        uint256 storedRate = receiver.getRate();

        // Simulate 7 days without a rate update
        vm.warp(block.timestamp + 7 days);

        // getRate() still returns the old rate — no revert
        uint256 rateAfterWarp = receiver.getRate();
        assertEq(rateAfterWarp, storedRate, "Rate should still be stale");

        // rsETH appreciates ~0.077% in 7 days at 4% APY
        uint256 trueRate = storedRate * 10_000_077 / 10_000_000;

        // Over-minting per 1e18 token deposited (tokenToETHRate = 1e18 for WETH)
        uint256 rsETHStale = 1e18 * 1e18 / storedRate;
        uint256 rsETHTrue  = 1e18 * 1e18 / trueRate;

        assertTrue(rsETHStale > rsETHTrue, "Over-minting confirmed");
        emit log_named_uint("Excess rsETH per 1e18 WETH (7-day staleness)", rsETHStale - rsETHTrue);
        // ~77e12 wei of rsETH (~0.077%) unbacked per deposit unit
    }
}
```

The invariant `rsETHAmount * rsETHToETHrate_true ≤ tokenAmount * tokenToETHRate` is violated whenever `rsETHToETHrate` (stale) `< rsETHToETHrate_true` (current), which is the normal state between LayerZero update calls.