### Title
Stale `rsETHPrice` Enables Yield Theft via Deposit-Before-Price-Update Attack - (File: contracts/LRTOracle.sol)

### Summary
`updateRSETHPrice()` is a public function with no timeout or deadline enforcement. The stored `rsETHPrice` used for deposits and withdrawals can be arbitrarily stale when staking rewards have accumulated. An attacker can deposit at the stale (lower) price to receive excess rsETH, then withdraw after the price is updated, capturing yield that belongs to existing rsETH holders.

### Finding Description
`LRTOracle.updateRSETHPrice()` is declared `public` with only a `whenNotPaused` guard — no role restriction, no timeout, and no requirement that it be called within any time window. [1](#0-0) 

Internally, `_updateRsETHPrice()` computes the new price as:

```
previousTVL = rsethSupply * rsETHPrice   // uses the STORED stale price
rewardAmount = totalETHInProtocol - previousTVL
newRsETHPrice = (totalETHInProtocol - protocolFeeInETH) / rsethSupply
``` [2](#0-1) 

The stored `rsETHPrice` state variable is only updated when `_updateRsETHPrice()` runs. Between calls, as staking rewards accrue, `totalETHInProtocol` grows while `rsETHPrice` stays frozen at its last-written value.

Deposits read this stale stored value directly:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

`updateRSETHPrice()` is never called atomically inside `depositETH`, `depositAsset`, or `initiateWithdrawal`. The deposit and withdrawal paths each independently read the stale `rsETHPrice` without triggering a refresh. [4](#0-3) 

Similarly, `initiateWithdrawal` calls `getExpectedAssetAmount(asset, rsETHUnstaked)` which also resolves through the stored oracle price, not a live computation. [5](#0-4) 

### Impact Explanation
**High — Theft of unclaimed yield.**

When `rsETHPrice` is stale (lower than the true value implied by accumulated rewards), a depositor receives more rsETH than their proportional share of the pool warrants. After `updateRSETHPrice()` is called and the price rises to reflect the accumulated rewards, the attacker's inflated rsETH balance redeems for more underlying assets than they deposited. The excess comes directly from the yield that should have accrued to pre-existing rsETH holders, diluting their share of the pool.

### Likelihood Explanation
**Medium.** Staking rewards (e.g., EigenLayer restaking yields, LST rebases) accumulate continuously. Any gap between consecutive `updateRSETHPrice()` calls — which is normal operational behavior since there is no enforced cadence — creates a window. The attacker only needs to:
1. Observe that `totalETHInProtocol` has grown beyond `rsethSupply * rsETHPrice` (readable on-chain).
2. Deposit before the price is refreshed.
3. Wait for the price update (or call it themselves if the increase is within `pricePercentageLimit`).
4. Withdraw at the higher price.

No privileged access is required. The `pricePercentageLimit` guard limits the per-update price jump for non-managers but does not eliminate the window — it only caps the per-transaction profit, making repeated smaller attacks viable. [6](#0-5) 

### Recommendation
1. **Short term**: Call `updateRSETHPrice()` atomically at the start of `depositETH`, `depositAsset`, and `initiateWithdrawal` so the price used for minting/redeeming is always fresh.
2. **Short term**: Add a staleness check — revert if `block.timestamp` exceeds the last price update timestamp by more than a configurable threshold (e.g., 1 hour).
3. **Long term**: Consider a commit-reveal or time-weighted price mechanism so that a single block's deposit cannot immediately benefit from a price update in the same or next block.

### Proof of Concept
1. Staking rewards accumulate over several hours. `totalETHInProtocol` = 10,100 ETH; `rsethSupply` = 10,000; stored `rsETHPrice` = 1.00 ETH (stale). True price ≈ 1.01 ETH.
2. Attacker calls `depositETH{value: 100 ether}()`. `getRsETHAmountToMint` computes `100 * 1e18 / 1.00e18 = 100 rsETH`. At the true price the attacker should receive ≈ 99.01 rsETH. The attacker receives ~1% excess.
3. Anyone (or the attacker) calls `updateRSETHPrice()`. `rsETHPrice` updates to ≈ 1.01 ETH (within the daily threshold, so no revert for a non-manager).
4. Attacker calls `initiateWithdrawal(ETH, 100 rsETH)`. `getExpectedAssetAmount` returns `100 * 1.01e18 / 1e18 = 101 ETH`. The attacker recovers 101 ETH having deposited 100 ETH, extracting 1 ETH of yield from existing holders. [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L85-89)
```text
    /// @notice updates RSETH/ETH exchange rate
    /// @dev calculates rsETH price based on stakedAsset value received from EigenLayer
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

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L162-178)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```
