### Title
Depositor Can Exploit Stale `rsETHPrice` by Frontrunning `updateRSETHPrice()` to Steal Accrued Yield from Existing rsETH Holders - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function. Between calls, the stored `rsETHPrice` is stale. When EigenLayer rewards accrue and increase the protocol's TVL, the rsETH price should rise — but it does not until `updateRSETHPrice()` is explicitly called. An attacker can deposit at the stale (lower) price, receive more rsETH than they are entitled to, and then trigger the price update, effectively stealing the accrued yield from all existing rsETH holders.

---

### Finding Description

`LRTOracle` stores a cached `rsETHPrice` that is only updated when `updateRSETHPrice()` is called:

```solidity
// contracts/LRTOracle.sol:87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

This function is **public and callable by anyone**. Between calls, `rsETHPrice` reflects the TVL at the time of the last update, not the current TVL.

`LRTDepositPool.getRsETHAmountToMint()` reads this cached price directly to determine how many rsETH tokens to mint for a depositor:

```solidity
// contracts/LRTDepositPool.sol:520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

Because `rsETHPrice` is in the denominator, a **stale lower price** causes the depositor to receive **more rsETH** than the current TVL justifies.

The attack flow:

1. EigenLayer rewards accrue, increasing the protocol's TVL. The true rsETH price is now `P_new > P_old`, but `rsETHPrice` in storage still holds `P_old`.
2. The attacker calls `LRTDepositPool.depositETH()` or `depositAsset()` with a large amount `Y`. They receive `Y * assetPrice / P_old` rsETH — more than the fair share `Y * assetPrice / P_new`.
3. The attacker (or any keeper) calls `updateRSETHPrice()`, which updates `rsETHPrice` to `P_new`.
4. The attacker's rsETH now represents a larger share of the protocol than their deposit warranted. All pre-existing rsETH holders are diluted by exactly the amount the attacker over-received.

There is no atomic price refresh inside `depositETH` or `depositAsset`, and no staleness guard on `rsETHPrice` at deposit time.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders earn yield as EigenLayer rewards increase the protocol's TVL. This yield is reflected in a rising `rsETHPrice`. By depositing at the stale lower price, the attacker captures a portion of that yield before it is priced in, diluting every existing holder proportionally. The stolen amount per attack is:

```
stolen ≈ deposit_amount × (P_new − P_old) / P_old
```

For a large depositor and a long staleness window (e.g., days of accrued rewards), this can be material. The attack is repeatable every time rewards accrue and the price has not yet been updated.

---

### Likelihood Explanation

**Medium.**

- `updateRSETHPrice()` is not called atomically with reward accruals; there is always a window of staleness.
- The attacker does not need to frontrun a specific mempool transaction — they only need to observe on-chain state (e.g., EigenLayer strategy balances) to know rewards have accrued and the price is stale.
- No special role or permission is required; any EOA with capital can execute this.
- The attacker can also frontrun a pending `updateRSETHPrice()` transaction in the mempool to guarantee ordering.

---

### Recommendation

1. **Refresh price atomically before minting**: Call `_updateRsETHPrice()` (or an equivalent internal read of the live TVL) inside `_beforeDeposit` before computing `rsethAmountToMint`, so deposits always use the current price.
2. **Staleness guard**: Revert deposits if `rsETHPrice` has not been updated within a configurable maximum staleness window (e.g., 1 hour).
3. **Commit-reveal or deposit delay**: Introduce a delay between deposit initiation and rsETH minting (analogous to the existing `withdrawalDelayBlocks`), so the price used for minting reflects the state after the deposit is committed.

---

### Proof of Concept

```
State before attack:
  rsETHPrice (stored) = 1.00 ETH  (stale — not yet updated)
  True rsETH price    = 1.01 ETH  (rewards accrued, TVL increased by 1%)

Step 1: Attacker calls depositETH{value: 10_000 ETH}(minRSETH=0, "")
  rsethAmountToMint = 10_000e18 * 1e18 / 1.00e18 = 10_000 rsETH
  (fair amount would be: 10_000e18 * 1e18 / 1.01e18 ≈ 9_901 rsETH)

Step 2: Attacker (or keeper) calls LRTOracle.updateRSETHPrice()
  rsETHPrice updated to 1.01 ETH

Step 3: Attacker holds 10_000 rsETH, each worth 1.01 ETH
  Attacker's position value = 10_100 ETH
  Attacker deposited        = 10_000 ETH
  Profit                    ≈ 100 ETH — stolen from existing holders
```

The `depositETH` entry point is unrestricted: [1](#0-0) 

The rsETH mint amount is computed using the cached stale price: [2](#0-1) 

The price update function is public and permissionless: [3](#0-2) 

The price is computed from live TVL only when `_updateRsETHPrice()` is called, not on every deposit: [4](#0-3)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-251)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

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

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```
