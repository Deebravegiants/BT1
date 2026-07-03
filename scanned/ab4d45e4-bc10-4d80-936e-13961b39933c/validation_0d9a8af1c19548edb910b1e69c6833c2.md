Based on my research, I found a valid analog vulnerability in the LRT-rsETH codebase.

---

### Title
Stale `rsETHPrice` Used in Deposit Minting Allows Users to Claim Yield They Did Not Earn - (`contracts/LRTDepositPool.sol`)

### Summary
`LRTDepositPool.depositETH` and `depositAsset` mint rsETH using the stored `LRTOracle.rsETHPrice`, which is never refreshed atomically before a deposit. If staking rewards have accrued since the last `updateRSETHPrice()` call, a depositor receives more rsETH than they are entitled to, diluting existing holders' yield.

### Finding Description

`LRTOracle.rsETHPrice` is a state variable that must be explicitly updated by calling `updateRSETHPrice()` (or its manager variant). It is **not** called inside the deposit path. [1](#0-0) 

The deposit flow in `LRTDepositPool` calls `_beforeDeposit`, which calls `getRsETHAmountToMint`: [2](#0-1) 

`getRsETHAmountToMint` divides by the **stored** `rsETHPrice`: [3](#0-2) 

`_updateRsETHPrice` computes the true price from live TVL (`_getTotalEthInProtocol`) and the current rsETH supply. As EigenLayer/LST staking rewards accrue, `totalETHInProtocol` grows while `rsETHPrice` stays frozen at its last-written value: [4](#0-3) 

Because `rsETHPrice` is stale (lower than the true value), the division `amount * assetPrice / rsETHPrice` yields a **larger** rsETH amount than the depositor deserves. After the deposit, any caller can invoke `updateRSETHPrice()` to push the price to its correct (higher) value. The attacker's rsETH is now worth more than what they paid, at the expense of pre-existing holders whose share of the TVL was diluted.

This is structurally identical to the reference report: an update that should happen before share issuance is skipped (there, due to a rate-change threshold; here, because no update call exists in the deposit path at all), and the depositor captures yield that accrued before their entry.

### Impact Explanation

**High — Theft of unclaimed yield.**

Every rsETH holder's proportional claim on the protocol TVL is diluted. The attacker receives rsETH backed by more ETH than they deposited. The magnitude scales with (a) how long `updateRSETHPrice()` has not been called and (b) how much staking yield accrued in that window. Over hours or days without a price update, the stolen yield can be material.

### Likelihood Explanation

`updateRSETHPrice()` is a public function with no access restriction: [1](#0-0) 

It is not called on-chain by any keeper or by the deposit path itself. Any period without an off-chain bot update (network congestion, bot downtime, weekends) creates an exploitable window. MEV bots can monitor the mempool for pending `updateRSETHPrice()` transactions and front-run them with a large deposit, then back-run with a withdrawal after the price update.

### Recommendation

Call `updateRSETHPrice()` (or an internal equivalent) at the start of `depositETH` and `depositAsset` before computing `rsethAmountToMint`, analogous to how the reference report recommends using `previewAddInterest` to ensure fresh values before share issuance. This ensures the price used for minting always reflects the current TVL.

### Proof of Concept

1. Staking rewards accrue for several hours; `updateRSETHPrice()` has not been called. True rsETH price is, say, 1.005 ETH but stored `rsETHPrice` is still 1.000 ETH.
2. Attacker calls `depositETH{value: 100 ETH}(0, "")`.
   - `getRsETHAmountToMint` computes `100e18 * 1e18 / 1.000e18 = 100 rsETH`.
   - Correct amount would be `100e18 * 1e18 / 1.005e18 ≈ 99.5 rsETH`.
   - Attacker receives ~0.5 rsETH extra.
3. Attacker (or anyone) calls `updateRSETHPrice()`. Price updates to 1.005 ETH.
4. Attacker's 100 rsETH is now worth `100 * 1.005 = 100.5 ETH` — a profit of ~0.5 ETH funded by diluting existing holders. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-250)
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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
