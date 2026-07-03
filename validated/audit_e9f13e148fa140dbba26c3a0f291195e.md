### Title
Protocol Fee Charged on Yield Accrued During Pause Period — (`contracts/LRTOracle.sol`)

### Summary

`LRTOracle._updateRsETHPrice()` contains a `protocolPaused` guard that is intended to prevent protocol fee minting while the system is paused. However, this guard only prevents fee minting at the exact moment of the call. Because `updateRSETHPrice()` is blocked by `whenNotPaused` during a pause, the `rsETHPrice` is never updated during the pause period. When the protocol unpauses and `updateRSETHPrice()` is called, the fee is calculated against the stale pre-pause price, causing the full yield that accrued during the pause to be subject to the protocol fee — even though users could not withdraw or act during that time.

### Finding Description

`LRTOracle.updateRSETHPrice()` is gated by `whenNotPaused`: [1](#0-0) 

Inside `_updateRsETHPrice()`, the fee calculation compares the current TVL against a `previousTVL` derived from the stored `rsETHPrice`: [2](#0-1) 

The `protocolPaused` flag is evaluated at call time: [3](#0-2) 

Because `updateRSETHPrice()` cannot be called while the oracle is paused, `rsETHPrice` is never updated during the pause. When the protocol unpauses, the first call to `updateRSETHPrice()` computes `previousTVL` using the stale pre-pause price. All yield that accrued during the pause is included in `rewardAmount`, and the full protocol fee is charged on it — despite the comment stating fees should not be taken while paused.

The `updateRSETHPriceAsManager()` bypass exists but requires the `MANAGER` role: [4](#0-3) 

If the manager does not manually call this during the pause to update the price (which is the expected behavior during an emergency pause), the vulnerability is triggered automatically on the first public call after unpause.

### Impact Explanation

rsETH holders lose a portion of the yield that accrued during the pause period to protocol fees. The fee is minted as new rsETH to the treasury, diluting all existing holders. Users could not withdraw or rebalance during the pause, yet they bear the full fee on pause-period yield. This constitutes **theft of unclaimed yield** (High severity).

Concrete example: TVL = 1,000,000 ETH, 30-day pause, 4% annual staking yield, 10% protocol fee → ~3,288 ETH of yield accrues during pause → ~329 ETH worth of rsETH minted to treasury as fee on yield users could not avoid.

### Likelihood Explanation

Every protocol pause where the oracle is also paused (the standard `pauseAll()` path pauses the oracle) and the manager does not manually call `updateRSETHPriceAsManager()` during the pause triggers this. Staking rewards accrue continuously, so any non-trivial pause duration produces measurable impact. The `pauseAll()` function in `LRTConfig` explicitly pauses the oracle: [5](#0-4) 

Likelihood is **Medium** — pauses are infrequent but the impact is automatic and requires no attacker action beyond calling the public `updateRSETHPrice()` after unpause.

### Recommendation

When the protocol unpauses, reset `rsETHPrice` to the current TVL-derived price **without charging a fee**, so that only yield accruing after the unpause is subject to the protocol fee. One approach: record the timestamp or block of the pause, and in `_updateRsETHPrice()`, skip the fee if the `previousTVL` baseline predates the most recent unpause event. Alternatively, call `_updateRsETHPrice()` (with fee suppressed) as part of the unpause flow to advance the price baseline before any fee-eligible call can occur.

### Proof of Concept

1. Protocol is running; `updateRSETHPrice()` is called, setting `rsETHPrice = P₀` and `highestRsethPrice = P₀`.
2. Admin calls `pauseAll()` — `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` are all paused.
3. 30 days pass. EigenLayer staking rewards accrue; `_getTotalEthInProtocol()` would now return `TVL₁ > TVL₀`. `rsETHPrice` remains `P₀` (no update possible).
4. Admin calls `unpause()` on all contracts.
5. Any user calls `updateRSETHPrice()`:
   - `previousTVL = rsethSupply * P₀` (stale, pre-pause value)
   - `totalETHInProtocol = TVL₁` (includes 30 days of rewards)
   - `protocolPaused = false`
   - `rewardAmount = TVL₁ - TVL₀` (entire pause-period yield)
   - `protocolFeeInETH = rewardAmount * protocolFeeInBPS / 10_000`
   - rsETH minted to treasury for the full fee on pause-period yield [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
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

**File:** contracts/LRTOracle.sol (L298-311)
```text
        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }
```

**File:** contracts/LRTConfig.sol (L262-285)
```text
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
        if (!rsETHContract.paused()) rsETHContract.pause();

        address[] memory nodeDelegatorQueue = ILRTDepositPool(address(lrtDepositPool)).getNodeDelegatorQueue();
        uint256 nodeDelegatorCount = nodeDelegatorQueue.length;

        for (uint256 i = 0; i < nodeDelegatorCount;) {
            IPausable nodeDelegator = IPausable(nodeDelegatorQueue[i]);
            if (!nodeDelegator.paused()) nodeDelegator.pause();
            unchecked {
                ++i;
            }
        }

        emit PausedAll(msg.sender);
    }
```
