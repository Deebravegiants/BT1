### Title
Stale `rsETHPrice` Allows Depositors to Dilute and Steal Accrued Yield from Existing rsETH Holders - (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function. Between calls, the stored `rsETHPrice` is stale. When staking rewards accrue and increase the protocol TVL, the actual per-share value of rsETH is higher than the stored price. An attacker can deposit at the stale (undervalued) price to receive more rsETH than they are entitled to, then trigger a price update, and exit at the corrected higher price — stealing a proportional share of the accrued yield from all existing rsETH holders.

---

### Finding Description

`LRTOracle` stores the rsETH exchange rate in the state variable `rsETHPrice`, which is only updated when `updateRSETHPrice()` is explicitly called:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [1](#0-0) 

This function is **public and callable by anyone**. Between calls, `rsETHPrice` is stale.

`LRTDepositPool.getRsETHAmountToMint()` uses this stale value directly to compute how many rsETH tokens to mint for a depositor:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

When staking rewards accrue (e.g., EigenLayer restaking rewards, ETH validator rewards received via `receiveFromRewardReceiver()`), the actual protocol TVL rises above `rsethSupply × rsETHPrice`. The stored price is therefore **lower than the true value**. A depositor at this moment receives **more rsETH than their ETH is worth at the true price**.

The `_updateRsETHPrice()` internal function computes the new price as:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [3](#0-2) 

After the attacker's deposit is included in `totalETHInProtocol`, the price update dilutes the reward increase across all rsETH holders — including the attacker's newly minted shares — transferring a portion of the accrued yield to the attacker.

The attacker does **not** need to front-run any pending transaction. They can:
1. Observe on-chain that TVL has grown beyond `rsethSupply × rsETHPrice` (rewards have accrued).
2. Call `depositETH()` or `depositAsset()` at the stale price.
3. Call `updateRSETHPrice()` themselves (if the price increase is within `pricePercentageLimit`), or wait for the protocol's automated updater.
4. Initiate withdrawal through `LRTWithdrawalManager` and claim after the queue delay. [4](#0-3) 

---

### Impact Explanation

**Theft of unclaimed yield — High severity.**

Existing rsETH holders accumulate yield as the protocol TVL grows. When an attacker deposits at a stale price, they dilute the pending yield: the price update is shared across a larger rsETH supply, so each existing holder receives less than they were entitled to. The attacker captures the difference upon exit.

Concretely:
- Existing supply: 1,000 rsETH; stale price: 1.000 ETH/rsETH; actual TVL: 1,010 ETH (10 ETH rewards accrued).
- Attacker deposits 1,000 ETH → receives 1,000 rsETH (at stale 1.000 rate).
- `updateRSETHPrice()` is called: new TVL = 2,010 ETH, new supply = 2,000 rsETH → new price = **1.005 ETH/rsETH**.
- Attacker withdraws 1,000 rsETH → receives **1,005 ETH**. Profit: **5 ETH**.
- Existing holders: their 1,000 rsETH is now worth 1,005 ETH instead of the 1,010 ETH they were owed. **Loss: 5 ETH** (half of all accrued rewards stolen).

The attack scales linearly with capital: a larger deposit steals a larger fraction of the pending yield.

---

### Likelihood Explanation

**Medium.** The attack is permissionless and requires no privileged access. The attacker only needs to:
- Monitor the on-chain state for reward accrual (publicly readable).
- Have sufficient ETH capital to make the attack profitable after gas and opportunity cost.
- Wait through the `LRTWithdrawalManager` queue delay (EigenLayer imposes a ~7-day delay for queued withdrawals).

At 5% APY, locking 1,000 ETH for 7 days costs ~0.96 ETH in opportunity cost, while stealing 5 ETH yields a net profit of ~4 ETH. The attack becomes more attractive the longer `updateRSETHPrice()` goes uncalled (larger accrued rewards) and the larger the attacker's capital.

---

### Recommendation

Call `_updateRsETHPrice()` (or enforce a freshness check on `rsETHPrice`) **inside `_beforeDeposit()`** before computing `getRsETHAmountToMint()`. This ensures every deposit uses the current, up-to-date exchange rate and eliminates the stale-price window that enables yield theft.

Alternatively, restrict `updateRSETHPrice()` to a trusted keeper/manager role so that the price cannot be updated on-demand by an attacker immediately after a large deposit.

---

### Proof of Concept

**Setup:**
- rsETH total supply: 1,000 rsETH
- Stored `rsETHPrice`: 1.000 ETH (stale — not updated for 24 hours)
- Actual protocol TVL: 1,010 ETH (10 ETH in EigenLayer/validator rewards received via `receiveFromRewardReceiver()`)

**Attack steps:**

1. Attacker calls `LRTDepositPool.depositETH{value: 1000 ether}(minRSETH, "")`.
   - `getRsETHAmountToMint` computes: `1000e18 * 1e18 / 1.000e18 = 1000 rsETH`.
   - Attacker receives **1,000 rsETH**.

2. Attacker calls `LRTOracle.updateRSETHPrice()`.
   - `_getTotalEthInProtocol()` returns 2,010 ETH (1,010 existing + 1,000 from attacker).
   - New rsETH supply: 2,000.
   - `newRsETHPrice = 2010e18 / 2000 = 1.005e18`.
   - `rsETHPrice` is updated to **1.005 ETH/rsETH**.

3. Attacker initiates withdrawal of 1,000 rsETH via `LRTWithdrawalManager`.

4. After the withdrawal queue delay, attacker claims **1,005 ETH**.

**Result:**
- Attacker profit: **+5 ETH** (net of capital returned).
- Existing holders' 1,000 rsETH: worth 1,005 ETH instead of the 1,010 ETH they were owed.
- **5 ETH of accrued yield stolen** from existing rsETH holders in a single atomic sequence. [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L58-68)
```text
    receive() external payable { }

    /// @dev receive from RewardReceiver
    function receiveFromRewardReceiver() external payable { }

    /// @dev receive from LRTConverter
    function receiveFromLRTConverter() external payable { }

    /// @dev receive from NodeDelegator
    function receiveFromNodeDelegator() external payable { }

```

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
