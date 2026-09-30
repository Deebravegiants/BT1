# [H] Storage gap discrepancy during upgrade causes storage collision in vault controller strategies

## Summary
Severity: High
Contest weight: 0.7857
Dataset id: 21928
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Both [`CommunityVCS`](https://etherscan.io/address/0x96418d70832d08cf683be81ee9890e1337fad41b#code) and [`OperatorVCS`](https://etherscan.io/address/0x584338dabae9e5429c334fc1ad41c46ac007bc29#code) are upgradeable contracts that are already deployed on mainnet.

The contracts audited are intended to upgrade these. There is however an issue with the storage gap in the inherited contract `VaultControllerStrategy`:

The `VaultControllerStrategy` used as base in the deployed contracts have its storage setup like this:
```solidity
    IStaking public stakeController;       // 1
    Fee[] internal fees;                   // 2

    address public vaultImplementation;    // 3

    IVault[] internal vaults;              // 4
    uint256 internal totalDeposits;        // 5
    uint256 public totalPrincipalDeposits; // 6
    uint256 public indexOfLastFullVault;   // 7

    uint256 public maxDepositSizeBP;       // 8

    uint256[9] private __gap;              // 8 + 9 = 17
```

And in the upgraded code from `VaultControllerStrategy`:
```solidity
    IStaking public stakeController;               // 1
    Fee[] internal fees;                           // 2

    address public vaultImplementation;            // 3

    IVault[] internal vaults;                      // 4
    uint256 internal totalDeposits;                // 5
    uint256 public totalPrincipalDeposits;         // 6

    uint256 public maxDepositSizeBP;               // 7

    IFundFlowController public fundFlowController; // 8
    uint256 internal totalUnbonded;                // 9

    VaultGroup[] public vaultGroups;               // 10
    GlobalVaultState public globalVaultState;      // 11
    uint256 internal vaultMaxDeposits;             // 12

    uint256[6] private __gap;                      // 12 + 6 = 18!
```

There are four new slots added, `totalUnbonded`, `vaultGroups`, `globalVaultState` and `vaultMaxDeposits` however the gap is only decreased by 3 (`9` -> `6`). Hence the total storage slots used by the upgraded `VaultControllerStrategy` will increase by `1` encroaching on the storage of the `Community` and `OperatorVCS` implenentations.

Note, there is also some variables that have been moved and renamed (`maxDepositSizeBP` and `indexOfLastFullVault`) but that is handled in the `initializer`

For `CommunityVCS` the impact is quite moderate. This is the storage `CommunityVCS`:
```solidity
contract CommunityVCS is VaultControllerStrategy {
    uint128 public vaultDeploymentThreshold;
    uint128 public vaultDeploymentAmount;
```
The extra gap will lead to that `vaultDeploymentThreshold` will get the value of `vaultDeploymentAmount` (`6` on chain at time of writing). And `vaultDeploymentAmount` will be `0`.

These are used in `CommunityVCS::performUpkeep`:
```solidity
    function performUpkeep(bytes calldata) external {
        if ((vaults.length - globalVaultState.depositIndex) >= vaultDeploymentThreshold)
            revert VaultsAboveThreshold();
        _deployVaults(vaultDeploymentAmount);
    }
```
Since `vaultDeploymentAmount` is `0` no new vaults will be deployed until the issue is discovered and the values updated (using `setVaultDeploymentParams`).

This will at most cause deposits to be blocked for a while since no new vaults will be deployed.

For `OperatorVCS` however, the impact is more severe:
Here's the storage layout of `OperatorVCS`:
```solidity
contract OperatorVCS is VaultControllerStrategy {
    using SafeERC20Upgradeable for IERC20Upgradeable;

    uint256 public operatorRewardPercentage;
    uint256 private unclaimedOperatorRewards;
```
`operatorRewardPercentage` will get the value of `unclaimedOperatorRewards` (`4914838471043033862842`, `4.9e21` at time or writing).

This is used in `OperatorVault` to calculate the portion of the rewards earned that should go to the operator:
```solidity
            opRewards =
                (uint256(depositChange) *
                    IOperatorVCS(vaultController).operatorRewardPercentage()) /
                10000;
```
This is ultimately triggered by calling `StakingPool::updateStrategyRewards` that is in-turn called periodically by the protocol.  If `updateStrategyRewards` (which in turn calls `OperatorVault::updateDeposits`) is called before the storage collision is discovered, the `OperatorVaults` will be handing out an enormous amount of reward shares to the operators. This will greatly diminish the value of each share held by anyone else and any operator who withdraws these can take a lot of `LINK` from the pool.

`StakingPool::updateStrategyRewards` is also callable by anyone hence a malicious operator could figure this out and backrun the upgrade by calling this themselves.

## Recommendation
Considering reducing the storage gap in the upgraded `VaultControllerStrategy` to `5`
