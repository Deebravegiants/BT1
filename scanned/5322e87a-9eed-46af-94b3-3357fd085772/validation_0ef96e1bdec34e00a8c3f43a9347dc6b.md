### Title
EigenLayer AVS Rewards Sent to Treasury Instead of rsETH Holders, Causing Permanent Loss of Yield - (`contracts/NodeDelegator.sol`)

### Summary

`NodeDelegator.processClaim` routes all EigenLayer AVS reward tokens to `lrtConfig.eigenLayerRewardReceiver()` — a separately configured treasury address — rather than back into the protocol's asset pool. Because the LRTOracle computes the rsETH exchange rate solely from assets held by NodeDelegators and EigenLayer strategies, these claimed reward tokens are never reflected in the rsETH price. Every rsETH holder permanently loses their proportional share of EigenLayer AVS rewards.

### Finding Description

Users deposit ETH and LSTs into `LRTDepositPool`, which forwards them to `NodeDelegator` contracts that stake the assets into EigenLayer strategies. EigenLayer's `RewardsCoordinator` periodically makes AVS reward tokens claimable by each staker (earner). The earner for all protocol-staked assets is the `NodeDelegator` contract itself.

`NodeDelegator` exposes a `processClaim` function:

```solidity
// contracts/NodeDelegator.sol lines 202-209
function processClaim(IRewardsCoordinator.RewardsMerkleClaim calldata claim)
    external
    nonReentrant
    onlyLRTOperator
    whenNotPaused
{
    IRewardsCoordinator(lrtConfig.rewardsCoordinator()).processClaim(claim, lrtConfig.eigenLayerRewardReceiver());
}
```

The `recipient` argument is hardcoded to `lrtConfig.eigenLayerRewardReceiver()`, which is a separately configured address set by the admin via:

```solidity
// contracts/LRTConfig.sol lines 204-211
function setEigenLayerRewardReceiver(address _eigenLayerRewardReceiver)
    external
    onlyRole(LRTConstants.DEFAULT_ADMIN_ROLE)
{
    UtilLib.checkNonZeroAddress(_eigenLayerRewardReceiver);
    eigenLayerRewardReceiver = _eigenLayerRewardReceiver;
    emit SetEigenLayerRewardReceiver(_eigenLayerRewardReceiver);
}
```

This `eigenLayerRewardReceiver` is a distinct address from the `LRTDepositPool` and from the `REWARD_RECEIVER` contract key in `LRTConstants`. Reward tokens transferred to it are never deposited back into any EigenLayer strategy, never added to the NodeDelegator's tracked balance, and therefore never included in the LRTOracle's total-asset calculation that determines the rsETH exchange rate. The rewards are permanently diverted away from rsETH holders.

### Impact Explanation

Every rsETH holder loses their proportional share of EigenLayer AVS rewards. These rewards are real, periodically distributed ERC-20 tokens (e.g., EIGEN, AVS-specific tokens) that accrue to the NodeDelegator as the registered staker. Because they are routed to a treasury address and never reflected in the rsETH price, rsETH holders receive a lower effective yield than they are entitled to. This matches the **High — Theft of unclaimed yield** impact category.

### Likelihood Explanation

EigenLayer's `RewardsCoordinator` is live and actively distributes rewards to stakers. The KelpDAO protocol has multiple NodeDelegators staking significant TVL into EigenLayer strategies. The `processClaim` path is already implemented and callable by the operator, meaning rewards will be claimed regularly — but they will always be diverted to the treasury. Every claim event is a yield-theft event for rsETH holders. Likelihood is **High**.

### Recommendation

Reward tokens claimed from EigenLayer should be re-deposited into the protocol's asset pool (or converted to a supported LST and deposited) so they increase the total assets backing rsETH and are reflected in the exchange rate. Alternatively, if the protocol intends to take a fee on EigenLayer rewards, only the fee portion should go to `eigenLayerRewardReceiver`, with the remainder re-deposited. The current design unconditionally diverts 100% of AVS rewards away from rsETH holders with no on-chain distribution mechanism.

### Proof of Concept

1. Alice deposits 10 stETH into `LRTDepositPool` and receives rsETH.
2. The NodeDelegator stakes Alice's stETH into the EigenLayer stETH strategy.
3. An AVS distributes 1000 EIGEN tokens to the NodeDelegator as the registered staker.
4. The operator calls `NodeDelegator.processClaim(claim)`.
5. `IRewardsCoordinator.processClaim(claim, lrtConfig.eigenLayerRewardReceiver())` transfers 1000 EIGEN to the treasury address.
6. The LRTOracle's `getTotalAssetDeposits` reads only EigenLayer strategy balances and NodeDelegator ETH balances — EIGEN tokens at the treasury are invisible to it.
7. The rsETH exchange rate is unchanged. Alice's rsETH is worth exactly what it was before the claim.
8. Alice has permanently lost her proportional share of the 1000 EIGEN reward. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/NodeDelegator.sol (L202-209)
```text
    function processClaim(IRewardsCoordinator.RewardsMerkleClaim calldata claim)
        external
        nonReentrant
        onlyLRTOperator
        whenNotPaused
    {
        IRewardsCoordinator(lrtConfig.rewardsCoordinator()).processClaim(claim, lrtConfig.eigenLayerRewardReceiver());
    }
```

**File:** contracts/LRTConfig.sol (L204-211)
```text
    function setEigenLayerRewardReceiver(address _eigenLayerRewardReceiver)
        external
        onlyRole(LRTConstants.DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(_eigenLayerRewardReceiver);
        eigenLayerRewardReceiver = _eigenLayerRewardReceiver;
        emit SetEigenLayerRewardReceiver(_eigenLayerRewardReceiver);
    }
```

**File:** contracts/utils/LRTConstants.sol (L20-29)
```text
    bytes32 public constant REWARD_RECEIVER = keccak256("REWARD_RECEIVER");
    bytes32 public constant PROTOCOL_TREASURY = keccak256("PROTOCOL_TREASURY");
    bytes32 public constant PUBKEY_REGISTRY = keccak256("PUBKEY_REGISTRY");
    bytes32 public constant UNLOCKED_WITHDRAWAL_INITIALIZER = keccak256("UNLOCKED_WITHDRAWAL_INITIALIZER");

    bytes32 public constant BEACON_CHAIN_ETH_STRATEGY = keccak256("BEACON_CHAIN_ETH_STRATEGY");
    bytes32 public constant EIGEN_STRATEGY_MANAGER = keccak256("EIGEN_STRATEGY_MANAGER");
    bytes32 public constant EIGEN_POD_MANAGER = keccak256("EIGEN_POD_MANAGER");
    bytes32 public constant EIGEN_DELEGATION_MANAGER = keccak256("EIGEN_DELEGATION_MANAGER");
    bytes32 public constant EIGEN_REWARDS_COORDINATOR = keccak256("EIGEN_REWARDS_COORDINATOR");
```
