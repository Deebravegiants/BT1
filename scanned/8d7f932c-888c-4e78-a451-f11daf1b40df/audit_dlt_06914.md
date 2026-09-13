# [M] L2SharedBridge l1LegacyBridge is not set

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-zksync
Published: 2024-03-28
Source: https://github.com/code-423n4/2024-03-zksync-findings/issues/77
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-03-zksync/blob/4f0ba34f34a864c354c7e8c47643ed8f4a250e13/code/contracts/zksync/contracts/bridge/L2SharedBridge.sol#L68


# Vulnerability details

## Vulnerability details

The migration steps for `L1ERC20Bridge/L2ERC20Bridge` are as follows:

https://github.com/code-423n4/2024-03-zksync/blob/main/docs/Protocol%20Section/Migration%20process.md

> II. Upgrade L1ERC20Bridge contract
> 
> 1. Upgrade L2 bridge
> 
> The new L2ERC20Bridge will upgraded to become the L2SharedBridge, and it will be backwards compatible with all messages from the old L1ERC20Bridge, so we upgrade that first as L1->L2 messages are much faster, and in the meantime we can upgrade the L1ERC20Bridge. The new L2SharedBridge can receive deposits from both the old L1ERC20Bridge and the new L1SharedBridge.
> 
> 2. Upgrade L1ERC20Bridge
> 
> We upgrade the L1ERC20Bridge, and move all ERC20 tokens to the L1SharedBridge.

Since `L2ERC20Bridge` will be updated first, and then `L1ERC20Bridge` will be updated, `L2SharedBridge` needs to be compatible with the old `L1ERC20Bridge` before `L1ERC20Bridge` is updated.

So in `L2SharedBridge.initialize()` we need to set `l1LegacyBridge = L1ERC20Bridge` and `finalizeDeposit()` to allow `l1LegacyBridge` to execute.

But the current implementation doesn't set `l1LegacyBridge`, it's always `address(0)`. 

```solidity
    function initialize(
        address _l1Bridge,
        address _l1LegecyBridge,
        bytes32 _l2TokenProxyBytecodeHash,
        address _aliasedOwner
    ) external reinitializer(2) {
        require(_l1Bridge != address(0), "bf");
        require(_l2TokenProxyBytecodeHash != bytes32(0), "df");
        require(_aliasedOwner != address(0), "sf");
        require(_l2TokenProxyBytecodeHash != bytes32(0), "df");

        l1Bridge = _l1Bridge;
        l2TokenProxyBytecodeHash = _l2TokenProxyBytecodeHash;

        if (block.chainid != ERA_CHAIN_ID) {
            address l2StandardToken = address(new L2StandardERC20{salt: bytes32(0)}());
            l2TokenBeacon = new UpgradeableBeacon{salt: bytes32(0)}(l2StandardToken);
            l2TokenBeacon.transferOwnership(_aliasedOwner);
        } else {
            require(_l1LegecyBridge != address(0), "bf2");
@>          // Missing set l1LegecyBridge？
            // l2StandardToken and l2TokenBeacon are already deployed on ERA, and stored in the proxy
        }
    }
```

The above method just checks `_l1LegecyBridge ! = address(0)`, and does not assign a value, `l1LegacyBridge` is always `adddress(0)`.

This way any messages sent by the user before update `L1ERC20Bridge` will fail because `finalizeDeposit()` will not pass the validation

## Impact

Until `L1ERC20Bridge` is updated, messages sent by the user will fail.

## Recommended Mitigation

```diff
    function initialize(
        address _l1Bridge,
        address _l1LegecyBridge,
        bytes32 _l2TokenProxyBytecodeHash,
        address _aliasedOwner
    ) external reinitializer(2) {
...
        if (block.chainid != ERA_CHAIN_ID) {
            address l2StandardToken = address(new L2StandardERC20{salt: bytes32(0)}());
            l2TokenBeacon = new UpgradeableBeacon{salt: bytes32(0)}(l2StandardToken);
            l2TokenBeacon.transferOwnership(_aliasedOwner);
        } else {
            require(_l1LegecyBridge != address(0), "bf2");
+           l1LegacyBridge = _l1LegecyBridge
            // l2StandardToken and l2TokenBeacon are already deployed on ERA, and stored in the proxy
        }
    }
```


## Assessed type

Context
