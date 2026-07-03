### Title
First Depositor Captures All Pre-Deposit Protocol Assets via Zero-Supply Price Initialization — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` unconditionally sets `rsETHPrice = 1 ether` whenever `rsethSupply == 0`, regardless of how many assets are already held in the protocol. Any ETH or LSTs that accumulate in `LRTDepositPool` before the first rsETH is minted are invisible to the price calculation at that moment. The first depositor receives rsETH at the stale 1 ether rate; after the price is updated to reflect the real backing, their rsETH is worth more than they deposited, letting them drain the pre-existing assets.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` contains the following early-return branch: [1](#0-0) 

```solidity
if (rsethSupply == 0) {
    rsETHPrice = 1 ether;
    highestRsethPrice = 1 ether;
    return;
}
```

This branch fires whenever `rsethSupply == 0` — at protocol launch, or after all rsETH has been redeemed — and it **ignores the actual ETH value held in the protocol**. The stored `rsETHPrice` is pinned to `1 ether` no matter how many assets are sitting in `LRTDepositPool`.

`LRTDepositPool.getRsETHAmountToMint` uses this stored price directly: [2](#0-1) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`LRTDepositPool` can accumulate ETH before any rsETH is minted through several permissionless or semi-permissionless paths: [3](#0-2) 

```solidity
receive() external payable { }
function receiveFromRewardReceiver() external payable { }
function receiveFromLRTConverter() external payable { }
function receiveFromNodeDelegator() external payable { }
```

`_getTotalEthInProtocol()` counts `address(this).balance` of the deposit pool as part of total ETH: [4](#0-3) 

```solidity
ethLyingInDepositPool = address(this).balance;
```

So after the first deposit, when `updateRSETHPrice()` is called with a non-zero supply, the new price is:

```
newRsETHPrice = (deposited_ETH + pre_existing_ETH) / rsethSupply
```

This is higher than `1 ether`, and the first depositor's rsETH is now worth more than they paid.

---

### Impact Explanation

**High — Theft of pre-deposit protocol assets.**

Any ETH or LSTs that enter `LRTDepositPool` before the first rsETH mint (e.g., from reward receivers, direct transfers, or node delegator returns) are effectively gifted to the first depositor. The depositor can deposit a dust amount of ETH, receive rsETH at the artificially low `1 ether` rate, wait for `updateRSETHPrice()` to be called (which is public and callable by anyone), and then withdraw at the updated, higher price — extracting the pre-existing assets.

---

### Likelihood Explanation

**Low-Medium.**

The window exists at two points in the protocol lifecycle:

1. **Protocol launch**: Before any user deposits, ETH may arrive via `receiveFromRewardReceiver()`, `receiveFromNodeDelegator()`, or direct `receive()` calls. This is a realistic operational scenario.
2. **After full redemption**: If all rsETH is burned and residual assets remain (e.g., EigenLayer rewards that arrived after the last withdrawal was processed), the next depositor faces the same condition.

No special privileges are required; the attacker only needs to be the first depositor after one of these states is reached.

---

### Recommendation

When `rsethSupply == 0`, compute the actual ETH backing before defaulting to `1 ether`. If `_getTotalEthInProtocol()` returns a non-zero value, the price should be set to reflect that backing rather than `1 ether`. Alternatively, block deposits when `rsethSupply == 0` and `totalETHInProtocol > 0` until an admin explicitly seeds the protocol with an initial deposit that accounts for the pre-existing assets.

```solidity
if (rsethSupply == 0) {
    uint256 totalETH = _getTotalEthInProtocol();
    if (totalETH == 0) {
        rsETHPrice = 1 ether;
        highestRsethPrice = 1 ether;
    }
    // else: do not update price; block deposits or require admin action
    return;
}
```

---

### Proof of Concept

1. Protocol is deployed; `rsETHPrice = 0`, `rsethSupply = 0`.
2. `updateRSETHPrice()` is called (public) → `rsETHPrice = 1 ether` (supply is 0).
3. 100 ETH arrives in `LRTDepositPool` via `receiveFromRewardReceiver()`.
4. Attacker calls `depositETH(1 ether, "")` with `msg.value = 1 ether`.
   - `getRsETHAmountToMint` → `(1e18 * 1e18) / 1e18 = 1e18` → mints **1 rsETH**.
5. Attacker calls `updateRSETHPrice()`:
   - `rsethSupply = 1e18`
   - `totalETHInProtocol = 101 ETH`
   - `newRsETHPrice = 101e18 / 1e18 = 101 ether`
6. Attacker requests withdrawal of 1 rsETH → receives **101 ETH**, stealing the 100 ETH that was pre-deposited. [5](#0-4) [6](#0-5) [3](#0-2)

### Citations

**File:** contracts/LRTOracle.sol (L214-222)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTDepositPool.sol (L58-67)
```text
    receive() external payable { }

    /// @dev receive from RewardReceiver
    function receiveFromRewardReceiver() external payable { }

    /// @dev receive from LRTConverter
    function receiveFromLRTConverter() external payable { }

    /// @dev receive from NodeDelegator
    function receiveFromNodeDelegator() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-481)
```text
        ethLyingInDepositPool = address(this).balance;

```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
