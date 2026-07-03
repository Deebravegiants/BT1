### Title
EigenLayer AVS Rewards Claimed to `eigenLayerRewardReceiver` With No On-Chain Distribution Path to rsETH Holders - (`contracts/NodeDelegator.sol`)

---

### Summary

`NodeDelegator.processClaim()` claims EigenLayer AVS restaking rewards and routes them unconditionally to `lrtConfig.eigenLayerRewardReceiver()`. There is no on-chain mechanism in the protocol to route these rewards back into the TVL or distribute them to rsETH holders, who are the beneficial owners of the restaked assets. The rewards are permanently diverted away from rsETH holders.

---

### Finding Description

`NodeDelegator.processClaim()` is the sole on-chain path for claiming EigenLayer AVS rewards:

```solidity
// contracts/NodeDelegator.sol L202-209
function processClaim(IRewardsCoordinator.RewardsMerkleClaim calldata claim)
    external
    nonReentrant
    onlyLRTOperator
    whenNotPaused
{
    IRewardsCoordinator(lrtConfig.rewardsCoordinator()).processClaim(claim, lrtConfig.eigenLayerRewardReceiver());
}
```

The recipient is hardcoded to `lrtConfig.eigenLayerRewardReceiver()`, an admin-configured address set via `LRTConfig.setEigenLayerRewardReceiver()`. [1](#0-0) [2](#0-1) 

The protocol has two reward-routing mechanisms:

1. **MEV/execution-layer rewards**: `FeeReceiver.sol` receives ETH and its `sendFunds()` function routes it to `LRTDepositPool`, increasing TVL and benefiting rsETH holders proportionally.
2. **EigenLayer AVS rewards**: Claimed via `processClaim()` and sent to `eigenLayerRewardReceiver` — an address with no corresponding in-scope contract that distributes rewards back to rsETH holders or increases TVL. [3](#0-2) 

The `LRTDepositPool.getETHDistributionData()` comment explicitly acknowledges that rewards are only accounted for once moved from `feeReceiver/rewardReceiver` to the deposit pool — but EigenLayer AVS rewards never take this path: [4](#0-3) 

There is no contract in scope that acts as `eigenLayerRewardReceiver` and routes EigenLayer rewards back into the protocol TVL. The rewards are sent out of the protocol's accounting perimeter entirely.

---

### Impact Explanation

rsETH holders are the beneficial owners of assets restaked into EigenLayer strategies and EigenPods. EigenLayer AVS rewards represent yield generated on those assets. By routing all claimed rewards to `eigenLayerRewardReceiver` — an address outside the TVL accounting system — rsETH holders permanently lose their entitled share of EigenLayer restaking yield. This constitutes **theft of unclaimed yield** (High severity).

---

### Likelihood Explanation

Every invocation of `NodeDelegator.processClaim()` by the operator diverts rewards away from rsETH holders. As EigenLayer AVS reward programs grow, the magnitude of diverted yield increases. The operator is incentivized to call this regularly, making the impact continuous and compounding.

---

### Recommendation

Route claimed EigenLayer rewards through the same path as MEV rewards: send them to `LRTDepositPool` (or `FeeReceiver`) so they are included in TVL and benefit rsETH holders proportionally. Specifically, change the recipient in `processClaim()` from `eigenLayerRewardReceiver` to the deposit pool address, or create a dedicated distributor contract (analogous to `FeeReceiver`) that accepts EigenLayer reward tokens and routes them into the TVL.

---

### Proof of Concept

1. EigenLayer AVS distributes rewards; `NodeDelegator` is the earner (staker).
2. Operator calls `NodeDelegator.processClaim(claim)`.
3. `IRewardsCoordinator.processClaim(claim, eigenLayerRewardReceiver)` transfers reward tokens to `eigenLayerRewardReceiver`.
4. `eigenLayerRewardReceiver` is an admin-set address with no in-protocol distribution logic.
5. `LRTDepositPool.getTotalAssetDeposits()` / `LRTOracle.rsETHPrice()` are unaffected — the rewards never enter TVL.
6. rsETH holders receive zero benefit from EigenLayer AVS rewards despite their assets generating them. [1](#0-0) [2](#0-1) [3](#0-2) [5](#0-4)

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

**File:** contracts/FeeReceiver.sol (L52-58)
```text
    /// @dev send all rewards to deposit pool
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L464-500)
```text
    /// @dev provides ETH amount distribution data among depositPool, NDCs and eigenLayer
    /// @dev rewards are not accounted here
    /// it will automatically be accounted once it is moved from feeReceiver/rewardReceiver to depositPool
    function getETHDistributionData()
        public
        view
        override
        returns (
            uint256 ethLyingInDepositPool,
            uint256 ethLyingInNDCs,
            uint256 ethStakedInEigenLayer,
            uint256 ethUnstakingFromEigenLayer,
            uint256 ethLyingInConverter,
            uint256 ethLyingInUnstakingVault
        )
    {
        ethLyingInDepositPool = address(this).balance;

        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;

        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
    }
```
