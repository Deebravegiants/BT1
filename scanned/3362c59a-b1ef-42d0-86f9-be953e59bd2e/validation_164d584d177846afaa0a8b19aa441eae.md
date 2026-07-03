Now I have all the information needed. Let me confirm the `getETHDistributionData` flow and the oracle's fee minting logic.### Title
Unpermissioned `sendFunds()` in `FeeReceiver` Allows Anyone to Inject ETH as Protocol Rewards, Triggering Unauthorized Fee Minting and rsETH Price Manipulation - (File: `contracts/FeeReceiver.sol`)

---

### Summary

`FeeReceiver.sendFunds()` has no access control. Any unprivileged caller can first send ETH to `FeeReceiver` (via its open `receive()`) and then call `sendFunds()` to flush that ETH into `LRTDepositPool` as if it were legitimate MEV/execution-layer rewards. Because `LRTDepositPool.getETHDistributionData()` counts `address(this).balance` verbatim, the injected ETH immediately inflates the protocol's reported TVL. When `LRTOracle.updateRSETHPrice()` is subsequently called, the oracle treats the TVL increase as organic yield, computes a protocol fee on it, and mints that fee as rsETH to the treasury — diluting every existing rsETH holder.

---

### Finding Description

`FeeReceiver` is the designated recipient of MEV and execution-layer rewards for the Kelp DAO restaking protocol. Its `receive()` function accepts ETH from any sender, and `sendFunds()` forwards the entire contract balance to `LRTDepositPool.receiveFromRewardReceiver()`:

```solidity
// contracts/FeeReceiver.sol L49-58
receive() external payable { }

function sendFunds() external {          // ← no access control
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

`sendFunds()` carries no `onlyRole` or similar guard. Once the ETH lands in `LRTDepositPool`, it is counted in `getETHDistributionData()`:

```solidity
// contracts/LRTDepositPool.sol L480
ethLyingInDepositPool = address(this).balance;
```

`getTotalAssetDeposits(ETH_TOKEN)` aggregates this value and passes it up to `LRTOracle._getTotalEthInProtocol()`. Inside `_updateRsETHPrice()`, the oracle computes:

```solidity
// contracts/LRTOracle.sol L244-246
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

The injected ETH is indistinguishable from real yield, so `rewardAmount` is inflated by exactly the attacker's donation. The oracle then mints rsETH to the treasury:

```solidity
// contracts/LRTOracle.sol L301-307
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
if (rsethAmountToMintAsProtocolFee > 0) {
    IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
}
```

A secondary effect: if `pricePercentageLimit` is configured, a sufficiently large injection can push `newRsETHPrice` above `highestRsethPrice * (1 + pricePercentageLimit)`, causing every non-manager call to `updateRSETHPrice()` to revert with `PriceAboveDailyThreshold`, temporarily freezing oracle updates.

---

### Impact Explanation

**Primary — High: Theft of unclaimed yield.**
The protocol fee is computed as a percentage of the apparent TVL increase. By donating ETH through `FeeReceiver`, an attacker forces the oracle to treat that donation as organic yield and extract a protocol fee from it. The fee is minted as rsETH to the treasury, diluting all existing rsETH holders. The dilution is proportional to `protocolFeeInBPS` applied to the injected amount. Holders receive less ETH per rsETH than they would have absent the attack.

**Secondary — Medium: Temporary freezing of funds.**
If `pricePercentageLimit` is set, a large enough injection causes `updateRSETHPrice()` to revert for all non-manager callers, blocking oracle updates until a manager intervenes. During this window, the stale rsETH price is used for all deposit and withdrawal calculations.

---

### Likelihood Explanation

The attack requires only ETH and a public function call — no special role, no governance capture, no front-running dependency. The cost to the attacker is the donated ETH (permanently locked in the protocol), but the damage to holders scales with `protocolFeeInBPS`. At a 10% protocol fee, donating 10 ETH causes 1 ETH worth of rsETH to be minted to the treasury at holders' expense. The attack is economically rational for a competitor or griever willing to spend ETH to harm the protocol's reputation or exhaust the daily fee mint cap.

---

### Recommendation

1. **Add access control to `sendFunds()`**: restrict it to `LRTConstants.MANAGER` or a dedicated operator role, matching the pattern used by other privileged fund-movement functions in the codebase.

```solidity
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

2. **Optionally restrict `receive()`**: accept ETH only from known node operators or the EigenLayer withdrawal path, rejecting arbitrary senders.

---

### Proof of Concept

```
1. Attacker calls FeeReceiver.receive() with 100 ETH (or selfdestruct-forces ETH in).
2. Attacker calls FeeReceiver.sendFunds() — no role check, succeeds.
   → LRTDepositPool.receiveFromRewardReceiver{value: 100 ether}() is called.
   → LRTDepositPool.balance increases by 100 ETH.
3. Anyone calls LRTOracle.updateRSETHPrice().
   → _getTotalEthInProtocol() returns previous TVL + 100 ETH.
   → rewardAmount = 100 ETH.
   → protocolFeeInETH = 100 ETH * protocolFeeInBPS / 10_000.
     (e.g., at 1000 BPS = 10%: protocolFeeInETH = 10 ETH)
   → newRsETHPrice = (totalETHInProtocol - 10 ETH) / rsethSupply  [inflated]
   → rsethAmountToMintAsProtocolFee = 10 ETH / newRsETHPrice
   → Treasury receives extra rsETH; all existing holders are diluted.
4. If pricePercentageLimit is set and 100 ETH pushes price above threshold:
   → updateRSETHPrice() reverts for non-managers until manager intervenes.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/FeeReceiver.sol (L49-58)
```text
    /// @dev fallback to receive funds
    receive() external payable { }

    /// @dev send all rewards to deposit pool
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L479-480)
```text
    {
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTOracle.sol (L243-247)
```text
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
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
