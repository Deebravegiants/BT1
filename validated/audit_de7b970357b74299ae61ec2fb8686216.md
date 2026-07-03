### Title
rsETH Inflation Attack via ETH Donation to `LRTDepositPool` Enables Zero-Share Minting - (File: `contracts/LRTDepositPool.sol`)

### Summary

An attacker who is the first depositor can donate ETH directly to `LRTDepositPool` and call the permissionless `updateRSETHPrice()` to inflate the stored `rsETHPrice`. Any subsequent depositor who passes `minRSETHAmountExpected = 0` will have their ETH accepted by the protocol while receiving 0 rsETH in return, permanently freezing their funds.

### Finding Description

**Root cause — three cooperating weaknesses:**

**1. `rsETHPrice` is inflatable via direct ETH donation**

`LRTOracle._updateRsETHPrice()` computes the new price as:

```
newRsETHPrice = totalETHInProtocol.divWad(rsethSupply)
``` [1](#0-0) 

`totalETHInProtocol` is built by `_getTotalEthInProtocol()`, which calls `ILRTDepositPool.getTotalAssetDeposits(ETH)`, which in turn calls `getETHDistributionData()`. That function reads:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [2](#0-1) 

Because `LRTDepositPool` exposes a bare `receive()`:

```solidity
receive() external payable { }
``` [3](#0-2) 

any ETH sent directly to the contract is immediately counted in TVL.

**2. `updateRSETHPrice()` is public and uncapped when `pricePercentageLimit == 0`**

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [4](#0-3) 

The only guard against a large price jump is:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [5](#0-4) 

`pricePercentageLimit` is a storage variable that defaults to `0`. When it is `0`, the condition short-circuits to `false` and the price can be inflated by any arbitrary multiple in a single call.

**3. `_beforeDeposit` does not reject a zero-rsETH mint**

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [6](#0-5) 

There is no `require(rsethAmountToMint > 0)`. If the caller passes `minRSETHAmountExpected = 0`, the check `0 < 0` is `false` and the deposit proceeds. `RSETH.mint(victim, 0)` does not revert (OpenZeppelin `_mint` with amount 0 is a no-op), so the victim's ETH is accepted and 0 rsETH is minted. [7](#0-6) 

**The mint formula:**

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [8](#0-7) 

After inflation, `rsETHPrice` is `(1 + X) * 1e18`. For a victim deposit `Y` where `Y < 1 + X`, integer division yields `rsethAmountToMint = 0`.

### Impact Explanation

**Critical — permanent freezing of user funds.**

The victim's ETH is transferred into `LRTDepositPool` (it arrives as `msg.value` before any check can revert it), but 0 rsETH is minted. With no rsETH balance, the victim has no mechanism to initiate a withdrawal. Their ETH is permanently locked in the protocol. The attacker, holding the only 1 wei of rsETH, eventually redeems it for the entire pool balance (their donation + victim's deposit).

### Likelihood Explanation

**Medium.** The attacker must be the first depositor (or act when rsETH supply is negligibly small). On Ethereum mainnet, front-running the first legitimate deposit is straightforward. The victim must pass `minRSETHAmountExpected = 0`; this is the default for many integrations and scripts that omit slippage protection. The critical enabler — `pricePercentageLimit == 0` — is the contract's default state at deployment.

### Recommendation

1. **Enforce a non-zero mint amount.** Add `require(rsethAmountToMint > 0, "ZeroMint")` inside `_beforeDeposit` before the slippage check.
2. **Initialize `pricePercentageLimit` to a safe non-zero value** (e.g., 1%) during deployment so that a single `updateRSETHPrice()` call cannot inflate the price by an unbounded factor.
3. **Seed the pool at deployment.** Mint a small amount of rsETH to a dead address (e.g., `address(0xdead)`) during initialization so that `rsethSupply` is never 0 for an attacker-controlled first deposit.

### Proof of Concept

```
State: rsETHPrice = 1e18, pricePercentageLimit = 0, rsETH totalSupply = 0

Step 1 — Attacker deposits 1 wei ETH:
  depositETH{value: 1}(minRSETHAmountExpected=0, "")
  rsethAmountToMint = (1 * 1e18) / 1e18 = 1
  → Attacker receives 1 wei rsETH. rsETH totalSupply = 1.

Step 2 — Attacker donates X ETH directly to LRTDepositPool:
  (bool ok,) = address(lrtDepositPool).call{value: X}("");
  → LRTDepositPool.balance = 1 + X

Step 3 — Attacker calls LRTOracle.updateRSETHPrice():
  totalETHInProtocol = 1 + X
  newRsETHPrice = (1 + X) * 1e18 / 1 = (1 + X) * 1e18
  pricePercentageLimit == 0 → no revert
  → rsETHPrice = (1 + X) * 1e18

Step 4 — Victim deposits Y ETH (Y ≤ X) with minRSETHAmountExpected = 0:
  rsethAmountToMint = (Y * 1e18) / ((1 + X) * 1e18) = Y / (1 + X) = 0
  0 < 0 → no revert
  RSETH.mint(victim, 0) → victim receives 0 rsETH
  → Victim's Y ETH is in the pool; victim has no rsETH to withdraw with.

Step 5 — Attacker redeems 1 wei rsETH:
  Attacker's 1 wei rsETH represents 100% of supply.
  Attacker recovers 1 + X + Y ETH.
  Net attacker profit: Y ETH (victim's entire deposit).
```

### Citations

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

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/RSETH.sol (L229-240)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }
```
