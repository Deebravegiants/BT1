# [M] 5.3.3 pairTokenBaseandpoolBasetemplate contracts instances are not initialized

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** PoolFactory.sol#L66-L81, PoolToken.sol#L9-L14, ERC20_Cloneable.sol#L33-L72,
LeveragedPool.sol#L90-L

**Description:** TheconstructorofPoolFactorycontract creates three template contract instances but only one is
initialized:poolCommitterBase. The other two contract instances (pairTokenBaseandpoolBase) are not initial-
ized.

```
contract PoolFactory is IPoolFactory, Ownable {
constructor(address _feeReceiver) {
...
PoolToken pairTokenBase = new PoolToken(DEFAULT_NUM_DECIMALS);// not initialized
pairTokenBaseAddress = address(pairTokenBase);
LeveragedPool poolBase = new LeveragedPool();// not initialized
poolBaseAddress = address(poolBase);
PoolCommitter poolCommitterBase = new PoolCommitter();// is initialized
poolCommitterBaseAddress = address(poolCommitterBase);
...
/* initialise base PoolCommitter template (with dummy values) */
poolCommitterBase.initialize(address(this), address(this), address(this), owner(), 0, 0, 0);
}
```
This means an attacker can initialize the templates setting them as the owner, and performowneractions on
contracts such as minting tokens. This can be misleading for users of the protocol as these minted tokens seem
to be valid tokens.

InPoolToken.initialize()an attacker can become the owner by callinginitialize()with an address under
his control as a parameter. The same can happen inLeveragedPool.initialize()with theinitialization
parameter.


```
contract PoolToken is ERC20_Cloneable, IPoolToken {
```
```
}
contract ERC20_Cloneable is ERC20, Initializable {
function initialize(address _pool, ) external initializer {// not called for the template contract
owner = _pool;
```
```
}
}
```
```
contract LeveragedPool is ILeveragedPool, Initializable, IPausable {
function initialize(ILeveragedPool.Initialization calldata initialization) external override
,! initializer {
// not called for the template contract
```
```
// set the owner of the pool. This is governance when deployed from the factory
governance = initialization._owner;
}
}
```
**Recommendation:** pairTokenBaseandpoolBaseshould be initialized with dummy values.

Consider using the upgradable versions of the OpenZeppelin ERC20 contracts, as they don’t have constructors.

**Tracer:** Valid, fixed in PR 396.

**Spearbit:** Acknowledged.
