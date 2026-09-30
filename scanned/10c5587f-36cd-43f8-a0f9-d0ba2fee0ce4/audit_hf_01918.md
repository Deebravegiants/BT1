# [M] Parent contract Factory.sol is missing storage gap which could lead to storage collisions if its upgraded

## Summary
Severity: Medium
Contest weight: 0.1127
Dataset id: 10536
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upgradeable parent contracts must implement a storage gap to allow the addition of
new state variables in the future without compromising the storage compatibility with existing deployments. Without a storage gap, if there are any new variables in the Factory.sol contract, they
will override variables in child contracts such as L1Factory.sol and L2Factory.sol. Recommendation:
```diff
@@ -26,6 +26,7 @@ abstract contract Factory is IFactory, OwnableUpgradeable,
PausableUpgradeable,
    mapping(address deployer => mapping(string protocol => mapping(string poolType =>
    address))) private _proxyPools;
    mapping(address deployer => DynamicSet.StringSet) private _protocols;
+
    uint256[46] __gap;
function __Factory_init() internal onlyInitializing {}
```

## Recommendation
No data
