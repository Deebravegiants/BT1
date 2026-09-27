# [M] Removed Plugin (simplePlugin) from StakingModule.sol can have unclaimed reward.

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L418-L430
Type: audit-issue

## Details
# Removed Plugin (simplePlugin) from StakingModule.sol can have unclaimed reward.

## Summary

Removed Plugin in StakingModule.sol can have unclaimed reward.

## Vulnerability Detail

In the current design, if the admin calls removePlugin, the plugin will just be removed.

```solidity
    /// @notice Removes a plugin
    function removePlugin(uint256 index) external onlyRole(PLUGIN_EDITOR_ROLE) {
        address plugin = plugins[index];

        pluginsMapping[plugin] = false;
        plugins[index] = plugins[nPlugins - 1];
        plugins.pop();
        nPlugins--;

        emit PluginRemoved(plugin, nPlugins);
    }
```

but the removed plugin can have unclaimed reward (tokens).

When the fee is swapped into TEL token, the funciton increaseClaimableBy is called, 
which  will pull TEL from the increaser

```solidity
function increaseClaimableBy(address account, uint256 amount) external onlyIncreaser returns (bool)
```

then the SimpluPlugin hold this token, and only the staking module can claim this reward.

```solidity
    function claim(address account, address to, bytes calldata) external override onlyStaking returns (uint256) {
```

note the modifier onlyStaking.

```solidity
    modifier onlyStaking() {
        require(msg.sender == address(staking), "SimplePlugin::onlyStaking: Caller is not StakingModule");
        _;
    }
```

Given that the staking module address is not changeable once it is set in the constructor, removing plugin from the staking module if the plugin has unclaimed reward means the reward is stucked in the SimplePlugin and no one can claim the token.

## Impact

Removed Plugin (simplePlugin) from StakingModule.sol can have unclaimed reward (fund stucked in the SimplePlugin)

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L418-L430

## Tool used

Manual Review

## Recommendation

We recommend add check to make sure that is no unclaimed reward in SimplePlugin before removing it.

```solidity
    /// @notice Removes a plugin
    function removePlugin(uint256 index) external onlyRole(PLUGIN_EDITOR_ROLE) {
        address plugin = plugins[index];

        require(IPlugin(plugin).totalClaimable() != 0, "has claimable reward");

        pluginsMapping[plugin] = false;
        plugins[index] = plugins[nPlugins - 1];
        plugins.pop();
        nPlugins--;

        emit PluginRemoved(plugin, nPlugins);
    }
```
