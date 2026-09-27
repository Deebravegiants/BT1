# [M] 7.16 Non 18 Decimals Protocol Tokens

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

The documentation states:

```
Decimals
```
```
To be consistent with the BASE chosen when computing numbers, it has been decided that all
the ERC20 tokens created by the Angle protocol would involve 18 decimals.
```
```
Although this is not specified anywhere in the code, this means that the base for agTokens
and sanTokens is 18.
```
The decimal of the sanToken however is set equal to the decimal of the underlying collateral. For
collaterals with decimals different than 18, the sanTokens decimal will not be equal to 18.

```
function initialize(
string memory name_,
string memory symbol_,
address poolManager
) public initializer {
__ERC20Permit_init(name_);
__ERC20_init(name_, symbol_);
stableMaster = IPoolManager(poolManager).stableMaster();
decimal = IERC20MetadataUpgradeable(IPoolManager(poolManager).token()).decimals();
}
```

Specification changed:

The developer documentation will be changed to accurately reflect this.
