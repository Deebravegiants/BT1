# [H] `addPlugin` function does not check for contract existence

## Summary
Severity: High
Reporter: 0xSmartContract
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417
Type: audit-issue

## Details
# `addPlugin` function does not check for contract existence

## Summary

The task of the `addPlugin` function in the `StakingModule.sol` contract is to add Plugins and these Plugins provide External Calls with contracts in many functions.
However, contract existence is not checked, so different levels of vulnerability may arise


## Vulnerability Detail

Security vulnerabilities that may arise due to not checking the plugin contract existence;
1 - A non-existent Plugin Contract can be added to `addPlugin`
2 - Plugin Contract with security vulnerability can be added (For example, a malicious code can be added to the `claim` function of the Plugin contract)
3 - A Plugin with a `selfdesctruct` function may have been added and then self-destruct, attempting to reach from the contract
4 - Codes that will consume all the gas can be added to the functions in the Plugin contract communicated with the external call.

Contract entity passes no security checks and only `PLUGIN_EDITOR_ROLE` is trusted, it is not behind a multisig and changes are not behind a time lock. so it has a "single point of failure" in this part

## Impact

Details of functions interacting with External Call and Plugin contracts;
```solidity
contracts/StakingModule.sol:
  107          for (uint256 i = 0; i < nPlugins; i++) {
  108:             total += IPlugin(plugins[i]).totalClaimable();

  146          for (uint256 i = 0; i < nPlugins; i++) {
  147:             total += IPlugin(plugins[i]).claimable(account, auxData);

  160          for (uint256 i = 0; i < nPlugins; i++) {
  161:             total += IPlugin(plugins[i]).claimableAt(account, blockNumber, auxData);

  269:         uint256 xClaimed = IPlugin(plugins[pluginIndex]).claim(account, to, auxData);

  296          for (uint256 i = 0; i < nPlugins; i++) {
  297:             total += IPlugin(plugins[i]).claim(account, to, auxData);
```

## Code Snippet

[StakingModule.sol#L409-L417](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417)

```solidity
contracts/StakingModule.sol:
  450      
  451:     function addPlugin(address plugin) external onlyRole(PLUGIN_EDITOR_ROLE) {
  452:         require(!pluginsMapping[plugin], "StakingModule::addPlugin: Cannot add an existing plugin");
  453: 
  454:         plugins.push(plugin);
  455:         pluginsMapping[plugin] = true;
  456:         nPlugins++;
  457: 
  458:         emit PluginAdded(plugin, nPlugins);
  459:     }
```

## Tool used

Manual Review

## Recommendation

1- Add timelock to the Plugin add process of the `PLUGIN_EDITOR_ROLE` role so that there is no "single point of failure" and manage it with a multisig wallet (Indicate this in the docs and NatSpec comments)
2- Check contract existence in `addPlugin` function
3- A detailed update can be made in the plugin adding procedure for the security concerns mentioned above.
