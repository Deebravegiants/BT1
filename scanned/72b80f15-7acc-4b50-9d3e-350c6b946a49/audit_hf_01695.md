# [M] Addresses are set to the 0 addr in constructor

## Summary
Severity: Medium
Contest weight: 0.5588
Dataset id: 9278
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the constructor the addresses for vaultManager and the StabilityPool are set. This is evident in the code snippet below.
```solidity
constructor() ERC20("KEI Stablecoin", "KEI", DECIMALS) {
    whitelisted[vaultManager] = true;
    whitelisted[stabilityPool] = true;
}
```

The problem is that during construction, the addresses have not yet been set and thus we are whitelisting zero addresses.

Below we can observe that the addresses are indeed set in the setAddresses function in AddressBook.sol:
```solidity
And because we must wait 2 weeks before we can whitelist the addresses in the addWhitelist function,
the protocol will be DOSed for 2 weeks. This can be observed below...
require(block.timestamp > requestedWhitelistTimestamp[_address] + TIMELOCK_DURATION, "Timelock period has not passed");
allowanceWhitelist[_address] = true;
mintWhitelist[_address] = true;
delete requestedWhitelistTimestamp[_address];
emit WhitelistChanged(_address, true);
```

Let us note that TIMELOCK_DURATION = 14 days.

## Recommendation
Set the addresses in the constructor before whitelisting said addresses in order to ensure the correct operation.
