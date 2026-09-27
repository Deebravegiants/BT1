# [M] ``_notifyStakeChangeAllPlugins`` call can DOS the protocol

## Summary
Severity: Medium
Reporter: imare
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L385-L389
Type: audit-issue

## Details
# ``_notifyStakeChangeAllPlugins`` call can DOS the protocol

## Summary
In case one of the used ``IPlugin`` contract reverts inside ``_notifyStakeChangeAllPlugins`` all main ``StableModule`` functions will also revert.

## Vulnerability Detail

``_notifyStakeChangeAllPlugins`` is used internally to notify all registered plugins when a account stake changes. This is done with the following for loop:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L385-L389

A ``IPlugin`` can signal his intention to be notified by returning ``true`` from the function ``requiresNotification()``

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/interfaces/IPlugin.sol#L10

## Impact
Inside the previously mentioned for loop this signal is ignored (commented out) so in a event a plugin chooses to ignore stakes changes callback by returning false in ``requiresNotification()`` and by reverting in the callback ``notifyStakeChange`` all main protocol functionality are denied.

## Code Snippet

## Tool used

Manual Review

## Recommendation
Uncomment the line 

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L387

or use try...catch to prevent misbehaving plugins from DOS-ing the protocol.
