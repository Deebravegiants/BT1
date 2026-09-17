# [M] Unbounded nPlugins can cause DOS to functions that uses it

## Summary
Severity: Medium
Reporter: koxuan
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L79-L89
Type: audit-issue

## Details
# Unbounded nPlugins can cause DOS to functions that uses it

## Summary
nPlugins is used in many functions such as `totalSupply` or `_claim`. It is used in loop control for for loops. As it is unbounded, it will consume more gas than the block limit if nPlugins is big and cause a revert.
## Vulnerability Detail
Let's take totalSupply as an example, nPlugins is unbounded. If it gets too big, the function will consume more gas than the block limit of 30 million. This will result in revert and therefore DOS to totalSupply(). There are also other functions like claim and claimable and many more. All of these functions that use nPlugins for for loops will have this problem. 
```solidity
    function totalSupply() external view returns (uint256) {
        uint256 total;

        // loop over all plugins and sum up totalClaimable
        for (uint256 i = 0; i < nPlugins; i++) {
            total += IPlugin(plugins[i]).totalClaimable();
        }
        
        // totalSupply is the total claimable from all plugins plus the total amount staked
        return total + _totalStaked;
    }
```
## Impact
User calling functions  that use nPlugins for for loops will revert when nPlugins is too big. 
## Code Snippet
[StakingModule.sol#L79-L89](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L79-L89)

```solidity
    function totalSupply() external view returns (uint256) {
        uint256 total;

        // loop over all plugins and sum up totalClaimable
        for (uint256 i = 0; i < nPlugins; i++) {
            total += IPlugin(plugins[i]).totalClaimable();
        }
        
        // totalSupply is the total claimable from all plugins plus the total amount staked
        return total + _totalStaked;
    }
```

## Tool used

Manual Review

## Recommendation
Set hard limit to nPlugins
```solidity
    function addPlugin(address plugin) external onlyRole(PLUGIN_EDITOR_ROLE) {
        require(!pluginsMapping[plugin], "StakingModule::addPlugin: Cannot add an existing plugin");

       //add check
       require (nPlugins+1 <= MAX_PLUGINS_ALLOWED);

        plugins.push(plugin);
        pluginsMapping[plugin] = true;
        nPlugins++;

        emit PluginAdded(plugin, nPlugins);
    }
```
