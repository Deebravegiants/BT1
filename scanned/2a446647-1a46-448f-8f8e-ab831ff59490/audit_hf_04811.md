# [M] Keep3r Relay Implementations are Not Com-

## Summary
Severity: Medium
Contest weight: 0.4351
Dataset id: 22681
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Keep3rRelay and Keep3rBondedRelay uses deprecated function for sidechains and exec calls will always revert.
Keep3r takes different arguments for function worked() in sidechains in order to estimate gas usage and rewards for keepers properly:
```solidity
/// @dev Sidechain implementation deprecates worked(address) as it should come with a usdPerGasUnit parameter
function worked(address) external pure override {
    revert Deprecated();
}
/// @dev Uses a USD per gas unit payment mechanism
/// @param _keeper Address of the keeper that performed the work
/// @param _usdPerGasUnit Units of USD (in wei) per gas unit that should be rewarded to the keeper
function worked(address _keeper, uint256 _usdPerGasUnit) external override {
```
The snippet above taken from Keep3rSidechain.sol that is live in optimism currently. We can also see that this contract is exact contract that will be interacted as it is the address of KEEPER_V2 in deployed Keep3r Relays by xKeeper in Optimism. Deployed addresses can checked from here But relay contracts
_execDataKeep3r[_execDataLength + 1] = IAutomationVault.ExecData({
    job: address(KEEP3R_V2),
    jobData: abi.encodeWithSelector(IKeep3rV2.worked.selector, msg.sender)
});
Hence in chains other than mainnet, Keep3r calls will always revert.
Current Keep3r Relay contracts are not compatible with Keep3r in Optimism (Keeper is only deployed to Mainnet and Optimism currently). Although vault creation will succeed, exec() called by keepers will always revert.

## Recommendation
Either implement a compatible version for Keep3rSideChain, or don't use Keep3r in sidechains.
