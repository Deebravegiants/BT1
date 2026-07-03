### Title
Attacker Can DOS Deposit Transactions by Donating ETH/LST to Inflate rsETH Price - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

### Summary
`LRTDepositPool` accepts ETH donations via an open `receive()` function and LST donations via direct ERC20 transfer. Because `getTotalAssetDeposits()` reads live contract balances and `updateRSETHPrice()` is a public, permissionless function, an attacker can donate a small amount of ETH or LST, call `updateRSETHPrice()` to commit the inflated TVL into the stored `rsETHPrice`, and cause any in-flight deposit whose `minRSETHAmountExpected` was computed against the pre-donation price to revert with `MinimumAmountToReceiveNotMet`.

### Finding Description

`LRTDepositPool` exposes an unrestricted `receive()` function:

```solidity
receive() external payable { }
```

`getETHDistributionData()` reads the live ETH balance of the deposit pool:

```solidity
ethLyingInDepositPool = address(this).balance;
```

`getAssetDistributionData()` reads the live ERC20 balance:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

Both are aggregated by `getTotalAssetDeposits()`, which feeds into `LRTOracle._getTotalEthInProtocol()`:

```solidity
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

`updateRSETHPrice()` is public and permissionless:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

`_updateRsETHPrice()` computes and stores a new price from the live TVL:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
...
rsETHPrice = newRsETHPrice;
```

`getRsETHAmountToMint()` divides by the stored `rsETHPrice`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`_beforeDeposit()` enforces the slippage guard:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

**Attack sequence:**
1. Victim submits `depositETH(minRSETHAmountExpected, referralId)` with `minRSETHAmountExpected` computed from the current `rsETHPrice`.
2. Attacker front-runs by sending a small amount of ETH directly to `LRTDepositPool` (or transferring LST tokens directly to the pool or any NodeDelegator address).
3. Attacker calls `updateRSETHPrice()`. The donated amount inflates `totalETHInProtocol`, raising `rsETHPrice`.
4. Victim's transaction executes. `getRsETHAmountToMint()` now returns fewer rsETH (higher denominator). The check `rsethAmountToMint < minRSETHAmountExpected` fails → revert.
5. Attacker repeats for every resubmission, maintaining the DOS indefinitely at low cost.

The `pricePercentageLimit` guard only blocks price increases that exceed the configured threshold in a single update. An attacker can stay within the threshold with a small donation while still exceeding the victim's slippage tolerance, or can make repeated small donations across multiple blocks to gradually ratchet the price upward.

### Impact Explanation

**Medium — Temporary freezing of funds.**

Legitimate depositors cannot complete deposits as long as the attacker continues to front-run with donations and price updates. Users are forced to resubmit with `minRSETHAmountExpected = 0` (removing slippage protection) or accept that every attempt will be griefed. The attacker loses the donated ETH/LST, but those funds accrue to existing rsETH holders, making the attack economically viable for a motivated griever. Deposits are temporarily frozen; no funds are permanently lost.

### Likelihood Explanation

**Medium.** The attack requires only:
- The ability to send ETH to `LRTDepositPool` (open `receive()`) or transfer any supported LST directly to the pool or a NodeDelegator.
- A single public call to `updateRSETHPrice()`.
- Mempool visibility to front-run a victim's deposit.

No privileged role, no oracle compromise, and no governance action is required. The cost per grief is the donated amount, which is recoverable in value by existing rsETH holders (including the attacker if they hold rsETH). The attack is repeatable and permissionless.

### Recommendation

1. **Separate accounting from live balances.** Introduce an internal accounting variable (analogous to the `takeBalanceSnapshot` fix described in TRST-H-2) that is only updated through official deposit/withdraw/transfer paths. Use this tracked balance in `getTotalAssetDeposits()` instead of raw `balanceOf()` / `address.balance` reads.
2. **Restrict `updateRSETHPrice()`.** Make it callable only by a trusted keeper or the LRT manager role, preventing an attacker from committing a donation-inflated price on demand.
3. **Alternatively**, ignore unaccounted ETH/LST balances in `getTotalAssetDeposits()` by tracking deposits and withdrawals explicitly, so that direct transfers to the pool have no effect on the oracle price.

### Proof of Concept

```
State before attack:
  rsETHPrice = 1.05e18 (stored)
  LRTDepositPool ETH balance = 100 ETH
  rsETH totalSupply = 95.24 rsETH

Victim submits:
  depositETH{value: 1 ETH}(minRSETHAmountExpected = 0.952e18, "")
  // expects ~0.952 rsETH at current price

Attacker front-runs:
  1. sends 0.5 ETH directly to LRTDepositPool  (receive() accepts it)
  2. calls updateRSETHPrice()
     totalETHInProtocol = 100.5 ETH  (includes donation)
     newRsETHPrice = 100.5e18 / 95.24 = ~1.0552e18
     rsETHPrice updated to 1.0552e18

Victim's tx executes:
  getRsETHAmountToMint(ETH, 1e18)
    = (1e18 * 1e18) / 1.0552e18
    = ~0.9477e18  (<  0.952e18 minRSETHAmountExpected)
  → revert MinimumAmountToReceiveNotMet
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTOracle.sol (L340-343)
```text
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
