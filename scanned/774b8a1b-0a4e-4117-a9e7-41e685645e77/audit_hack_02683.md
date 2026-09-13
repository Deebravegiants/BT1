# [M] There are various loops susceptible to DoS with block gas limit

## Summary
Severity: Medium
Reporter: catchup
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# There are various loops susceptible to DoS with block gas limit

## Summary
There are a few loops where the boundary of the loop is determined by a variable (```pluginCount```).

## Vulnerability Detail
Some of these loops don't have much gas usage, but some of them are a bit crowded. If the ```pluginCount``` grows too big in time, there is a chance that loops may cause a DoS.
The for loops within ```_ensureLinkAmount()```, ```_distributeToPlugins()``` and ```rebalancePlugins()``` are more dangerous as they have calls to other contract (plugin contract).

## Impact
If the ```pluginCount``` grows too big, ```deposit()``` and ```withdraw()``` to the vault will be impossible until some of the plugins are removed by the owner.

## Code Snippet
~~~
316:     function addPlugin(address _plugin, uint256 _index) external onlyOwner {
317:         require(_plugin != address(0), "Cannot add zero address");
318:         require(_index <= pluginCount, "Index must be less than or equal to plugin count");
319: 
320:         uint256 pointer = pluginCount;
321:         while (pointer > _index) {          //@audit-issue DoS
322:             plugins[pointer] = plugins[pointer - 1];
323:             pointer--;
324:         }
325:         plugins[pointer] = _plugin;
326:         pluginCount++;
327: 
328:         IERC20(LINK).approve(_plugin, type(uint256).max);
329: 
330:         emit PluginAdded(_plugin, _index);
331:     }
~~~

~~~
343:     function removePlugin(uint256 _index) external onlyOwner {
344:         require(_index < pluginCount, "Index out of bounds");
345:         address pluginAddr = plugins[_index];
346: 
347:         _withdrawFromPlugin(pluginAddr, IPlugin(pluginAddr).balance());
348: 
349:         uint256 pointer = _index;
350:         while (pointer < pluginCount - 1) {          //@audit-issue DoS
351:             plugins[pointer] = plugins[pointer + 1];
352:             pointer++;
353:         }
354:         delete plugins[pluginCount - 1];
355:         pluginCount--;
356: 
357:         IERC20(LINK).approve(pluginAddr, 0);
358: 
359:         emit PluginRemoved(pluginAddr);
360:     }
~~~

~~~
369:     function rebalancePlugins(uint256[] memory _withdrawalValues) external onlyOwner {
370:         require(_withdrawalValues.length == pluginCount, "Invalid withdrawal values");
371:         for (uint256 i = 0; i < pluginCount; i++) {          //@audit-issue DoS
372:             _withdrawFromPlugin(plugins[i], _withdrawalValues[i]);
373:         }
374:         _distributeToPlugins();
375:     }
~~~

~~~
458:     function _distributeToPlugins() internal {
459:         uint256 remaining = IERC20(LINK).balanceOf(address(this));
460: 
461:         // Plugins are ordered by priority. Fill the first one first, then the second, etc.
462:         for (uint256 i = 0; i < pluginCount; i++) {         //@audit-issue DoS
463:             if (remaining == 0) {
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

~~~
494:     function _ensureLinkAmount(uint256 _requested) internal {
495:         require(_requested <= availableForWithdrawal(), "Amount exceeds available balance");
496: 
497:         uint256 currentBalance = IERC20(LINK).balanceOf(address(this));
498:         if (currentBalance >= _requested) {
499:             return;
500:         }
501: 
502:         uint256 remaining = _requested - currentBalance;
503:         // Withdraw in reverse order of deposit
504:         for (uint256 i = 0; i < pluginCount; i++) {     //@audit-issue DoS
505:             if (remaining == 0) {
506:                 break;
507:             }
508: 
509:             address plugin = plugins[pluginCount - i - 1];
510:             uint256 available = IPlugin(plugin).availableForWithdrawal();
511:             if (available > 0) {
512:                 uint256 amount = available > remaining ? remaining : available;
513:                 _withdrawFromPlugin(plugin, amount);
514:                 remaining -= amount;
515:             }
516:         }
517: 
518:         if (remaining > 0) {
519:             revert("Unable to withdraw enough LINK from plugins");
520:         }
521:     }
~~~

## Tool Used
Manual review

## Recommendation
The max number of plugins to be added via ```addPlugin()``` can be limited by a defined ```MAX_PLUGIN_COUNT``` to ensure the loops would not be stretched too far in the future.
