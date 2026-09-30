# [M] Owner doesn't have to wait before whitelisting

## Summary
Severity: Medium
Contest weight: 0.6771
Dataset id: 9279
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Given that whitelisted addresses have a lot of power, the protocol wants to ensure a 14 day timelock is in place:
```
* @notice Given the admin key retains the ability to add debttoken
minters for future
Keiko_audit.md
deployments or upgrades a long timelock (14d) is
established.
* @dev Can only be called by the contract owner
```

The problem occurs because the owner does not need to wait the full TIMELOCK_DURATION when adding requestedWhitelistTimestamp as shown below:
```solidity
requestedWhitelistTimestamp[_address] = block.timestamp;
emit WhitelistRequested(_address, block.timestamp);
```

This variable is then used in the function addWhitelist:
```solidity
require(block.timestamp > requestedWhitelistTimestamp[_address] + TIMELOCK_DURATION, "Timelock period has not passed");
allowanceWhitelist[_address] = true;
mintWhitelist[_address] = true;
delete requestedWhitelistTimestamp[_address];
emit WhitelistChanged(_address, true);
```

The code is trying to enforce the 2 week timelock in the require statement.

The problem is that the owner can simply call addWhitelist first without calling requestWhitelist. Because the default value of uint256 is 0, then the require statement will pass and let the owner whitelist an address immediately.

## Recommendation
When requesting whitelist, suggest adding another variable, a mapping named whitelistRequested that tracks addresses to boolean. When the requestWhitelist function is called, set the variable, and require the value is true and therefore the TIMELOCK_DURATION is not compromised. A possible fix is shown below:
```solidity
require(block.timestamp > requestedWhitelistTimestamp[_address] + TIMELOCK_DURATION, "Timelock period has not passed");
require(whitelistRequested[_address], "Address has not been requested for whitelist");
```

Another potential fix that is more simple is to check that requestedWhitelistTimestamp[_address] > 0 in the addWhitelist function.
