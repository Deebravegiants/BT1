# [M] ```_distributeToPlugins()``` function may fail to distribute all LINK

## Summary
Severity: Medium
Reporter: catchup
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# ```_distributeToPlugins()``` function may fail to distribute all LINK


## Summary
```_distributeToPlugins()``` function may fail to distribute all of the vault balance if all the plugin addresses reach their MAX_CAPACITY.

## Vulnerability Detail
It is commented for the ```_distributeToPlugins()``` function that it "Distributes all LINK in the vault to the plugins". However, all the defined plugin addresses can reach to their MAX_CAPACITY while there is still ```remaining``` LINK.

## Impact
Owner may call ```rebalancePlugins()``` and think that the vault balance is distributed to the plugins in the most efficient way. 
However, there would be unallocated LINK in the vault which could have generated yield if allocated to a plugin. If owner knew this, he could have added a new plugin.

## Code Snippet
~~~
458:     function _distributeToPlugins() internal {
459:         uint256 remaining = IERC20(LINK).balanceOf(address(this));
460: 
461:         // Plugins are ordered by priority. Fill the first one first, then the second, etc.
462:         for (uint256 i = 0; i < pluginCount; i++) {
463:             if (remaining == 0) {                           //@audit-issue if all the plugings are full, this point will never be reached, remaining will be non-zero
464:                 break;
465:             }
466: 
467:             address plugin = plugins[i];
468:             uint256 available = IPlugin(plugin).availableForDeposit();
469:             if (available > 0) {
470:                 uint256 amount = available > remaining ? remaining : available;
471:                 _depositToPlugin(plugin, amount);
472:                 remaining -= amount;
473:             }
474:         }
475:     }
~~~


## Tool Used
Manual review

## Reccomendation
Consider having a success/fail return value for ```_distributeToPlugins()``` function, which would only return ```success``` when all the available LINK can be distributed to plugins. This way the caller function can be notified of the distribution status.
