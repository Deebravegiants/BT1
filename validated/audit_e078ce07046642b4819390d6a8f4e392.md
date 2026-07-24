### Title
Accumulated `nativeFee` ETH in `OmniBridge` Is Permanently Locked — No Withdrawal Mechanism Exists (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

Every call to `initTransfer` and `initTransfer1155` on the EVM `OmniBridge` contract accepts a `nativeFee` component inside `msg.value`. This ETH is intentionally retained in the contract (it is not forwarded to Wormhole or any other destination), yet the contract contains no function to withdraw or rescue accumulated ETH. The `nativeFee` ETH is permanently locked.

---

### Finding Description

In `OmniBridge.initTransfer`, the `msg.value` is split into two parts:

- **`extensionValue`** — the portion forwarded to `initTransferExtension` (and ultimately to Wormhole as its publishing fee).
- **`nativeFee`** — the remainder, which stays in the contract.

For ERC-20 transfers:
```
extensionValue = msg.value - nativeFee;   // line 393
```
For native ETH transfers:
```
extensionValue = msg.value - amount - nativeFee;   // line 391
```

The same split occurs in `initTransfer1155`:
```
extensionValue = msg.value - nativeFee;   // line 466
```

In `OmniBridgeWormhole.initTransferExtension`, only `value` (i.e., `extensionValue`) is forwarded to Wormhole:
```solidity
_wormhole.publishMessage{value: value}(...)   // line 143
```

The `nativeFee` ETH is never forwarded anywhere. It accumulates silently in the contract's balance with every bridging call that includes a non-zero `nativeFee`.

Searching the entire `OmniBridge.sol` for any ETH withdrawal path yields nothing. The only ETH-related function is:
```solidity
receive() external payable {}   // line 574
```
which accepts ETH but provides no way to retrieve it. There is no `withdraw`, `rescue`, `sweep`, or equivalent admin function.

---

### Impact Explanation

Every `initTransfer` or `initTransfer1155` call where `nativeFee > 0` permanently locks that ETH in the contract. This is protocol revenue (the `nativeFee` is the relayer/protocol fee denominated in the origin chain's native token) that can never be claimed. Over time, as the bridge processes volume, this constitutes an ever-growing, irreversibly frozen pool of ETH. This matches the "Critical — Irreversible fund lock, permanently unclaimable protocol value in fee flows" impact category.

---

### Likelihood Explanation

`initTransfer` is the primary public entry point for all EVM-side bridge transfers. Any user bridging tokens and specifying a non-zero `nativeFee` (which is the normal operating mode — the fee provider API quotes non-zero fees) triggers this. No special role or privilege is required. The accumulation is continuous and automatic.

---

### Recommendation

Add an admin-only ETH withdrawal function to `OmniBridge.sol`:

```solidity
function rescueETH(address payable destination) external onlyRole(DEFAULT_ADMIN_ROLE) {
    (bool sent, ) = destination.call{value: address(this).balance}("");
    require(sent, "ETH rescue failed");
}
```

Note: use `address(this).balance`, not `msg.value`, to access the accumulated contract balance — the exact mistake in the original InfinityExchange bug.

---

### Proof of Concept

1. User calls `OmniBridgeWormhole.initTransfer(tokenAddress, 1000, 0, 50, "alice.near", "")` with `msg.value = 50 + wormholeFee`.
2. Inside `initTransfer`: `extensionValue = msg.value - 50 = wormholeFee`. [1](#0-0) 
3. `initTransferExtension` is called with `value = wormholeFee`; Wormhole receives `wormholeFee`. [2](#0-1) 
4. The `50 wei` `nativeFee` remains in `OmniBridge`'s balance.
5. No function in `OmniBridge.sol` can move this ETH out. The only ETH-related declaration is `receive() external payable {}` which only accepts more ETH. [3](#0-2) 
6. Repeat for every bridging call. ETH accumulates and is permanently frozen.

The same applies to `initTransfer1155` at line 466. [4](#0-3)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L392-393)
```text
        } else {
            extensionValue = msg.value - nativeFee;
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L466-466)
```text
        uint256 extensionValue = msg.value - nativeFee;
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L574-574)
```text
    receive() external payable {}
```

**File:** evm/src/omni-bridge/contracts/OmniBridgeWormhole.sol (L143-147)
```text
        _wormhole.publishMessage{value: value}(
            wormholeNonce,
            payload,
            _consistencyLevel
        );
```
