### Title
Native `nativeFee` ETH Permanently Locked in `OmniBridge.sol` With No Withdrawal Path — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

Every `initTransfer` call that includes a non-zero `nativeFee` deposits ETH into the `OmniBridge` contract that can never be recovered. The `nativeFee` is subtracted from `extensionValue` before being passed to `initTransferExtension`, so it is never forwarded anywhere. No admin or protocol withdrawal function exists for accumulated native ETH, making it permanently locked.

---

### Finding Description

In `OmniBridge.sol::initTransfer`, the caller sends `msg.value` covering both the Wormhole messaging fee and the `nativeFee`. The contract computes:

```solidity
extensionValue = msg.value - nativeFee;   // ERC-20 path
// or
extensionValue = msg.value - amount - nativeFee;  // native ETH path
``` [1](#0-0) 

Only `extensionValue` is forwarded to `initTransferExtension`. In `OmniBridgeWormhole`, that extension calls:

```solidity
_wormhole.publishMessage{value: value}(wormholeNonce, payload, _consistencyLevel);
``` [2](#0-1) 

where `value = extensionValue` — the `nativeFee` portion is **not** forwarded. It remains in the contract's ETH balance.

The entire `OmniBridge.sol` contract contains no function to withdraw accumulated ETH. The only ETH-outflow path is `finTransfer` when `payload.tokenAddress == address(0)`, which sends ETH to a transfer recipient — not to any fee collector or admin. [3](#0-2) 

The contract also exposes a bare `receive()` that silently accepts additional ETH, further confirming there is no accounting or withdrawal mechanism for it. [4](#0-3) 

---

### Impact Explanation

Every `initTransfer` call with `nativeFee > 0` permanently locks that ETH in the contract. Because the contract is used for all cross-chain transfers that require a native-fee incentive for relayers, this accumulates over the entire protocol lifetime. The ETH is unclaimable by any party — user, relayer, or admin — through any currently deployed code path. This satisfies the **Critical** criterion: *"Irreversible fund lock… permanently unclaimable user or protocol value in bridge… fee… flows."*

---

### Likelihood Explanation

Any unprivileged user calling `initTransfer` with `nativeFee > 0` triggers the lock. This is the normal, documented relayer-incentive mechanism, so it is exercised on every transfer that uses a native fee. Likelihood is **High**.

---

### Recommendation

Add an admin-gated withdrawal function for accumulated native ETH, for example:

```solidity
function withdrawNativeFees(address payable to, uint256 amount)
    external
    onlyRole(DEFAULT_ADMIN_ROLE)
{
    (bool ok, ) = to.call{value: amount}("");
    require(ok, "ETH transfer failed");
}
```

Alternatively, track `nativeFee` accumulation in a dedicated storage variable and emit events so the locked amount is auditable.

---

### Proof of Concept

1. Alice calls `initTransfer(tokenAddress=USDC, amount=1000e6, fee=0, nativeFee=0.01 ether, recipient="alice.near", message="")` sending `msg.value = 0.01 ether` (Wormhole fee is 0 in this example).
2. Inside `initTransfer`: `extensionValue = 0.01 ether - 0.01 ether = 0`.
3. `initTransferExtension` is called with `value = 0`; Wormhole receives 0 ETH.
4. The contract's ETH balance increases by `0.01 ether`.
5. No function in `OmniBridge.sol` or `OmniBridgeWormhole.sol` can withdraw this ETH.
6. Repeated across all users over time, the locked ETH grows without bound and is permanently unclaimable. [5](#0-4) [6](#0-5)

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

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L373-437)
```text
    function initTransfer(
        address tokenAddress,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string calldata recipient,
        string calldata message
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

        emit BridgeTypes.InitTransfer(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message
        );
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L574-574)
```text
    receive() external payable {}
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
