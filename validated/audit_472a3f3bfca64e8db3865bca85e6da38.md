### Title
Accumulated `nativeFee` ETH in `OmniBridge` is permanently irretrievable — (`File: evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`OmniBridge.sol` collects a `nativeFee` in ETH on every `initTransfer` call, but never routes that ETH anywhere — it silently accumulates in the contract. Combined with an open `receive()` fallback and no sweep/withdrawal function, all collected native fees are permanently locked with no retrieval path.

---

### Finding Description

In `initTransfer`, when bridging ETH (`tokenAddress == address(0)`), the caller must send `msg.value >= amount + nativeFee`. The contract splits `msg.value` as follows:

```
extensionValue = msg.value - amount - nativeFee   // line 391
```

- `amount` is held in the contract to be paid out on `finTransfer`
- `extensionValue` is forwarded to Wormhole via `_wormhole.publishMessage{value: value}` in `OmniBridgeWormhole.initTransferExtension` (line 143)
- **`nativeFee` is never forwarded anywhere** — it stays in the contract [1](#0-0) [2](#0-1) 

The same pattern applies to ERC-20 `initTransfer` calls: `extensionValue = msg.value - nativeFee`, so again `nativeFee` stays in the contract while only `extensionValue` is forwarded to Wormhole. [3](#0-2) 

Additionally, the contract exposes an open `receive()` fallback, allowing anyone to send ETH directly to the contract with no accounting or recovery path. [4](#0-3) 

The only ETH egress in the entire contract is the `finTransfer` path for native ETH tokens (`payload.tokenAddress == address(0)`), which sends exactly `payload.amount` to the recipient — it does not touch accumulated `nativeFee` balances. [5](#0-4) 

There is no `sweep`, `withdraw`, or admin ETH-recovery function anywhere in `OmniBridge.sol` or `OmniBridgeWormhole.sol`. [6](#0-5) 

---

### Impact Explanation

Every `initTransfer` call that includes a non-zero `nativeFee` permanently locks that ETH in the contract. Over the lifetime of the bridge, this accumulates into a significant sum of protocol fee revenue that can never be claimed. This matches the **Critical** impact category: permanently unclaimable protocol value in bridge fee flows.

---

### Likelihood Explanation

`nativeFee` is a standard parameter of the public `initTransfer` entrypoint, callable by any unprivileged user. Every normal bridge transaction that includes a relayer fee contributes to the locked balance. This is a routine, high-frequency code path — not an edge case.

---

### Recommendation

Add an admin-only ETH withdrawal function to recover accumulated `nativeFee` and any ETH sent via `receive()`:

```solidity
function withdrawETH(address payable to, uint256 amount)
    external
    onlyRole(DEFAULT_ADMIN_ROLE)
{
    (bool success, ) = to.call{value: amount}("");
    if (!success) revert FailedToSendEther();
}
```

Alternatively, explicitly route `nativeFee` to a designated fee recipient inside `initTransfer` so it never accumulates in the contract.

---

### Proof of Concept

1. User calls `initTransfer(address(0), 1 ether, 0, 0.01 ether, "recipient", "")` sending `msg.value = 1.01 ether`.
2. `extensionValue = 1.01 ether - 1 ether - 0.01 ether = 0`.
3. `initTransferExtension` is called with `value = 0`; Wormhole receives `0` ETH.
4. `1 ether` is held for the eventual `finTransfer` payout.
5. `0.01 ether` (`nativeFee`) sits in the contract with no accounting entry and no withdrawal path.
6. After N such transactions, `N * 0.01 ether` is permanently locked.
7. Calling `address(omniBridge).balance` confirms the surplus; no function exists to recover it. [7](#0-6) [8](#0-7)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L317-322)
```text
        if (payload.tokenAddress == address(0)) {
            // slither-disable-next-line arbitrary-send-eth
            (bool success, ) = payload.recipient.call{value: payload.amount}(
                ""
            );
            if (!success) revert FailedToSendEther();
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L380-426)
```text
    ) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
        currentOriginNonce += 1;
        if (fee >= amount) {
            revert InvalidFee();
        }

        uint256 extensionValue;
        if (tokenAddress == address(0)) {
            if (fee != 0) {
                revert InvalidFee();
            }
            extensionValue = msg.value - amount - nativeFee;
        } else {
            extensionValue = msg.value - nativeFee;
            if (customMinters[tokenAddress] != address(0)) {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    customMinters[tokenAddress],
                    amount
                );
                ICustomMinter(customMinters[tokenAddress]).burn(
                    tokenAddress,
                    amount
                );
            } else if (isBridgeToken[tokenAddress]) {
                BridgeToken(tokenAddress).burn(msg.sender, amount);
            } else {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
            }
        }

        initTransferExtension(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message,
            extensionValue
        );

```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L548-596)
```text
    function pause(uint256 flags) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause(flags);
    }

    function pauseAll() external onlyRole(PAUSABLE_ADMIN_ROLE) {
        uint256 flags = PAUSED_FIN_TRANSFER |
            PAUSED_INIT_TRANSFER |
            PAUSED_DEPLOY_TOKEN;
        _pause(flags);
    }

    function upgradeToken(
        address tokenAddress,
        address implementation
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(isBridgeToken[tokenAddress], "ERR_NOT_BRIDGE_TOKEN");
        BridgeToken proxy = BridgeToken(tokenAddress);
        proxy.upgradeToAndCall(implementation, bytes(""));
    }

    function setNearBridgeDerivedAddress(
        address nearBridgeDerivedAddress_
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        nearBridgeDerivedAddress = nearBridgeDerivedAddress_;
    }

    receive() external payable {}

    function deriveDeterministicAddress(
        address tokenAddress,
        uint256 tokenId
    ) public pure returns (address) {
        return
            address(
                bytes20(keccak256(abi.encodePacked(tokenAddress, tokenId)))
            );
    }

    function _normalizeDecimals(uint8 decimals) internal pure returns (uint8) {
        uint8 maxAllowedDecimals = 18;
        if (decimals > maxAllowedDecimals) {
            return maxAllowedDecimals;
        }
        return decimals;
    }

    function _authorizeUpgrade(
        address newImplementation
    ) internal override onlyRole(DEFAULT_ADMIN_ROLE) {}
```

**File:** evm/src/omni-bridge/contracts/OmniBridgeWormhole.sol (L118-150)
```text
    function initTransferExtension(
        address sender,
        address tokenAddress,
        uint64 originNonce,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string calldata recipient,
        string calldata message,
        uint256 value
    ) internal override {
        bytes memory payload = bytes.concat(
            bytes1(uint8(MessageType.InitTransfer)),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(sender),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(tokenAddress),
            Borsh.encodeUint64(originNonce),
            Borsh.encodeUint128(amount),
            Borsh.encodeUint128(fee),
            Borsh.encodeUint128(nativeFee),
            Borsh.encodeString(recipient),
            Borsh.encodeString(message)
        );
        // slither-disable-next-line reentrancy-eth
        _wormhole.publishMessage{value: value}(
            wormholeNonce,
            payload,
            _consistencyLevel
        );

        wormholeNonce++;
    }
```
