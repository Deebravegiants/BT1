# [M] \[M03\] Unregistered parties

## Summary
Severity: Medium
Source: https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/oracle/implementation/Registry.sol#L49
Type: audit-issue

## Details
The `Registry` contract [tracks the parties](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/oracle/implementation/Registry.sol#L49) associated with each registered financial contract. It provides mechanisms for financial contracts to [initialize](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/oracle/implementation/Registry.sol#L80), [add](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/oracle/implementation/Registry.sol#L112), [remove](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/oracle/implementation/Registry.sol#L133) and [query](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/oracle/implementation/Registry.sol#L206) the party members.

However, the [ExpiringMultiParty contract](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/ExpiringMultiParty.sol) does not inform the registry when its parties change. In fact, the `ExpiringMultiPartyCreator` [sets the initial party member](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/ExpiringMultiPartyCreator.sol#L113-L116) to the address that triggers the deployment, whether or not that address is a party to the financial contract.

Consider updating the `Registry` contract whenever the `ExpiringMultiParty` contract’s participants change.

**Update:** _Fixed in [PR#1353](https://github.com/UMAprotocol/protocol/pull/1353). The participants are no longer tracked in the `Registry` contract. Note that the party-related functions still exist in the `Registry`, but they do not apply to `ExpiringMultiParty` contracts._
