#Audit Report

## Title
Block Stuffing Delays Emergency Deposit-Limit or Fee Reduction by Manager — (`contracts/LRTConfig.sol`)

## Summary

`updateAssetDepositLimit` and `setProtocolFeeBps` in `LRTConfig.sol` are single-SSTORE manager transactions with no timelock, commit-reveal, or priority-inclusion mechanism. A well-capitalised attacker can submit high-gas filler transactions to fill consecutive blocks, delaying these emergency config writes. During the delay window, `_beforeDeposit` in `LRTDepositPool.sol` continues to enforce the stale (higher) deposit limit, allowing deposits into an asset the manager intended to halt and accruing fees at a rate the manager intended to reduce.

## Finding Description

`updateAssetDepositLimit` performs a single storage write with no ordering guarantee: [1](#0-0) 

`setProtocolFeeBps` similarly performs a single storage write: [2](#0-1) 

Neither function has a timelock, commit-reveal scheme, or any on-chain mechanism guaranteeing inclusion within a bounded number of blocks. Deposit enforcement reads `lrtConfig.depositLimitByAsset(asset)` at call time: [3](#0-2) 

Until the manager's transaction is mined, `depositLimitByAsset[asset]` retains the old value, so `_beforeDeposit` continues to accept deposits up to the old limit: [4](#0-3) 

An attacker monitoring the mempool for an emergency `updateAssetDepositLimit(asset, 0)` or `setProtocolFeeBps(0)` can submit filler transactions (e.g., tight SSTORE loops) with a higher effective gas price that consume the full ~30M block gas limit, pushing the manager's transaction out of the block for K blocks. The `pauseAll()` emergency path is equally subject to this attack as it is also a mempool transaction: [5](#0-4) 

## Impact Explanation

**Low — Block stuffing.** During the delay window the protocol continues to accept deposits into an asset the manager intended to halt, and continues to collect fees at a rate the manager intended to reduce. No funds are directly stolen, but the protocol fails to deliver the emergency halt it promised. This matches the explicitly allowed impact: *"Low. Block stuffing."*

## Likelihood Explanation

Block stuffing on Ethereum mainnet requires filling ~30M gas per block, which is expensive but feasible for an attacker who profits from continued deposits into a compromised or over-limit asset. No privileged access is required — any EOA can submit filler transactions. The attack is repeatable across consecutive blocks and requires only mempool monitoring and sufficient ETH for gas. The manager has no on-chain fallback that bypasses the mempool for these specific config writes.

## Recommendation

1. **Operational runbook**: In an emergency, the `PAUSER_ROLE` should call `pauseAll()` before or instead of updating config values. Pausing the deposit pool is the fastest single-transaction mitigation and has the same block-stuffing exposure, but it is a simpler, lower-gas target.
2. **Private mempool**: Use Flashbots `eth_sendPrivateTransaction` or a similar private relay for emergency manager transactions so they cannot be displaced by filler transactions.
3. **Immediate-enforcement flag**: If the new deposit limit is lower than the current one, enforce it immediately via a flag (e.g., a `paused` state per asset) rather than relying solely on a storage write that must be mined.

## Proof of Concept

Foundry local fork test (no mainnet testing):

1. Fork mainnet state locally.
2. Manager submits `updateAssetDepositLimit(stETH, 0)` with base-fee priority.
3. Attacker submits N filler transactions each consuming ~29.9M gas per block (tight SSTORE loop) with a higher effective gas price.
4. Assert manager tx is not included for K blocks; assert `lrtConfig.depositLimitByAsset(stETH)` still equals the old value.
5. Assert `depositPool.depositAsset(stETH, amount, 0, "")` succeeds during the stuffed window because `_checkIfDepositAmountExceedesCurrentLimit` reads the stale limit.
6. After K blocks, manager tx lands; assert `depositAsset` now reverts with `MaximumDepositLimitReached`.

```solidity
contract BlockStuffingFiller {
    uint256[500] private _slots;
    function fill() external {
        for (uint256 i; i < 500; ++i) {
            _slots[i] = block.number; // 500 SSTOREs ≈ 10M gas
        }
    }
}
```

### Citations

**File:** contracts/LRTConfig.sol (L123-133)
```text
    function updateAssetDepositLimit(
        address asset,
        uint256 depositLimit
    )
        external
        onlyRole(LRTConstants.MANAGER)
        onlySupportedAsset(asset)
    {
        depositLimitByAsset[asset] = depositLimit;
        emit AssetDepositLimitUpdate(asset, depositLimit);
    }
```

**File:** contracts/LRTConfig.sol (L196-200)
```text
    function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
        if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
        protocolFeeInBPS = _protocolFeeInBPS;
        emit UpdateFee(_protocolFeeInBPS);
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

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```
