# [H] OsTokenConfig::constructor() - L27: No input validation for parameter `_owner`. Unless this is intended functionality, which I doubt, then (additionally) it's calling the wrong function from Ownable.sol contract, the correct function contains address(0) check.

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-09-05
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/134
Type: hats-finding

## Details
**Github username:** @dappconsulting
**Submission hash (on-chain):** 0xa01ed2f9efb22c5cc229db911375bdc18accea086d8d98d90112fc41aef12566
**Severity:** high

**Description:**
**Description**\

OsTokenConfig::constructor() - L27: No input validation for parameter `_owner`. Unless this is intended functionality, which I doubt, then (additionally) it's calling the wrong function from Ownable.sol contract, the correct function contains address(0) check.

Currently the `constructor()` is calling `_transferOwnership()` on L78 of Ownable.sol, this is incorrect.

The `constructor()` should be calling `transferOwnership()` on L69 in Ownable.sol instead.

Consequences: 

If value `address(0)` is intentionally/accidentally passed to parameter `_owner` in the constructor(), it will cause the DoS of all onlyOwner functions for this OsTokenConfig contract, and basically disable/DoS the configuring of the OsToken. 
As per dev notes in Ownable.sol: "Renouncing ownership will leave the contract without an owner, thereby disabling any functionality that is only available to the owner."

https://github.com/stakewise/v3-core/blob/9c30c45878397aa97918cbafcc6a62e4be4bbd4d/contracts/osToken/OsTokenConfig.sol#L20-L28

Recommendation:

Either call the correct function from Ownable.sol, i.e. `transferOwnership()` on L69, or keep the existing called function, i.e. `_transferOwnership()` on L78, but then add a zero address check in the constructor as per below:

```solidity
  constructor(address _owner, Config memory config) Ownable2Step() {
    updateConfig(config);
  + if (_owner == address(0)) revert Errors.ZeroAddress();
    _transferOwnership(_owner);   
  }
```

**Attack Scenario**\

The consequences should be self-explanatory in terms of DoS of the relevant functionality, as per protocol/dev's own comments:

"Renouncing ownership will leave the contract without an owner, thereby disabling any functionality that is only available to the owner."


_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/134_
