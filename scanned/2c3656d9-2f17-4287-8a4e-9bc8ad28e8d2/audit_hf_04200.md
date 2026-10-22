# [M] L2SharedBridge l1LegacyBridge is not set

## Summary
Severity: Medium
Contest weight: 0.4713
Dataset id: 21030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The migration steps for `L1ERC20Bridge/L2ERC20Bridge` are as follows:

II. Upgrade L1ERC20Bridge contract

  1. Upgrade L2 bridge

The new L2ERC20Bridge will upgraded to become the L2SharedBridge, and it will be backwards compatible with all messages from the old L1ERC20Bridge, so we upgrade that first as L1->L2 messages are much faster, and in the meantime we can upgrade the L1ERC20Bridge. The new L2SharedBridge can receive deposits from both the old L1ERC20Bridge and the new L1SharedBridge.

  2. Upgrade L1ERC20Bridge

We upgrade the L1ERC20Bridge, and move all ERC20 tokens to the L1SharedBridge.

Since `L2ERC20Bridge` will be updated first, and then `L1ERC20Bridge` will be updated, `L2SharedBridge` needs to be compatible with the old `L1ERC20Bridge` before `L1ERC20Bridge` is updated.

So in `L2SharedBridge.initialize()` we need to set `l1LegacyBridge = L1ERC20Bridge` and `finalizeDeposit()` to allow `l1LegacyBridge` to execute.

But the current implementation doesn’t set `l1LegacyBridge`, it’s always `address(0)`.

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

The above method just checks `_l1LegecyBridge != address(0)`, and does not assign a value, `l1LegacyBridge` is always `adddress(0)`.

This way any messages sent by the user before update `L1ERC20Bridge` will fail because `finalizeDeposit()` will not pass the validation

## Recommendation
```solidity
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
        l1LegacyBridge = _l1LegecyBridge;
        // l2StandardToken and l2TokenBeacon are already deployed on ERA, and stored in the proxy
    }
}
```
