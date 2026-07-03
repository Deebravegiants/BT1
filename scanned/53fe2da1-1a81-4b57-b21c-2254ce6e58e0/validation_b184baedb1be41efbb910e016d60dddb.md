### Title
`ScrollMessenger.sendETHToL1ViaBridge()` Passes Zero `gasLimit` to Scroll Bridge, Causing L1 Relay Failure - (File: contracts/bridges/ScrollMessenger.sol)

### Summary

`ScrollMessenger` hardcodes `gasLimit = 0` when calling `IScrollMessenger.sendMessage`, mirroring the exact root cause of M-02. The Scroll bridge records this zero gas limit and uses it when relaying the message on L1, causing the relay call to the `L1VaultV2` target to fail with out-of-gas, temporarily freezing all ETH bridged from Scroll L2.

### Finding Description

`ScrollMessenger.sendETHToL1ViaBridge()` calls the Scroll native bridge's `sendMessage` with a hardcoded `gasLimit` of `0`:

```solidity
// contracts/bridges/ScrollMessenger.sol, line 23
IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", 0, msg.sender);
//                                                                        ^
//                                                              gasLimit hardcoded to 0
```

The NatSpec comment claims this uses a "default gas limit," but the Scroll bridge has no such concept. The `gasLimit` parameter is described in `IScrollMessenger` as:

> `gasLimit` — Gas limit required to complete the message relay on corresponding chain. [1](#0-0) 

When the L1ScrollMessenger relays the message on Ethereum mainnet, it executes the call to the target (`l1VaultETHForL2Chain`) with the recorded gas limit of 0. A `call{gas: 0}` to `L1VaultV2` will fail even though `L1VaultV2.receive()` is a simple payable stub, because the EVM cannot execute any call with zero gas budget. [2](#0-1) [3](#0-2) 

The other OP-stack messengers (`OptimismMessenger`, `BaseMessenger`, `UnichainMessenger`) correctly use `DEFAULT_GAS_LIMIT = 200_000`. `ScrollMessenger` is the only one that passes zero. [4](#0-3) 

### Impact Explanation

Every call to `RSETHPoolV2.bridgeAssets()` on the Scroll deployment routes through `ScrollMessenger` and submits a zero-gas-limit message to the Scroll bridge. The L1 relay will fail for every such message. The bridged ETH is held in the Scroll bridge's escrow and cannot be delivered to `L1VaultV2` until the message is manually retried with a correct gas limit (if Scroll's bridge supports retry). This constitutes **temporary freezing of funds** for all ETH accumulated in the Scroll pool. [5](#0-4) 

### Likelihood Explanation

This triggers on every normal operational call to `RSETHPoolV2.bridgeAssets()` by the `BRIDGER_ROLE`. No attacker action is needed — the bug fires unconditionally whenever the bridger performs their routine duty. The Scroll deployment is live (README lists `RSETHPoolV2` at `0xb80deaecd7F4Bca934DE201B11a8711644156a0a` and `ScrollMessenger` at `0xf3a6Bcafc5639EA6cC01975Ee69FcD63F614fb08`).

### Recommendation

Replace the hardcoded `0` with a constant matching the other messenger contracts:

```solidity
uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
    if (msg.value != value) revert MismatchedMsgValue();
    IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", DEFAULT_GAS_LIMIT, msg.sender);
}
```

### Proof of Concept

1. ETH accumulates in `RSETHPoolV2` on Scroll L2.
2. `BRIDGER_ROLE` calls `RSETHPoolV2.bridgeAssets()`.
3. This calls `IL2Messenger(messenger).sendETHToL1ViaBridge{value: ethBalanceMinusFees}(l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees)`.
4. `ScrollMessenger.sendETHToL1ViaBridge` calls `IScrollMessenger(l2bridge).sendMessage{value: value}(target, value, "", 0, msg.sender)` — gasLimit is 0.
5. The Scroll bridge records the message with `gasLimit = 0` and emits `SentMessage(..., gasLimit: 0, ...)`.
6. On L1, `L1ScrollMessenger.relayMessageWithProof` executes `l1VaultETHForL2Chain.call{value: ethAmount, gas: 0}("")`.
7. The call fails (out of gas). The ETH remains locked in the Scroll bridge escrow. `FailedRelayedMessage` is emitted.
8. All ETH bridged from Scroll is temporarily frozen. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/interfaces/L2/IScrollMessenger.sol (L62-63)
```text
    /// @param gasLimit Gas limit required to complete the message relay on corresponding chain.
    function sendMessage(address target, uint256 value, bytes calldata message, uint256 gasLimit) external payable;
```

**File:** contracts/bridges/ScrollMessenger.sol (L13-24)
```text
contract ScrollMessenger is IL2Messenger, ReentrancyGuard {
    /**
     * @notice Bridge ETH from Scroll L2 to Ethereum Mainnet
     * @param l2bridge The address of the L2 bridge on Scroll
     * @param target The address of the target contract on L1
     * @param value The amount of ETH to send
     * @dev Gas limit is set to 0 to use the default gas limit
     */
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", 0, msg.sender);
    }
```

**File:** contracts/L1VaultV2.sol (L562-563)
```text
    /// @dev Handles direct ETH transfers from the L2 bridge
    receive() external payable { }
```

**File:** contracts/bridges/OptimismMessenger.sol (L15-16)
```text
    /// @notice The recommended gas limit for sending ETH to L1 via the Optimism bridge
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;
```

**File:** contracts/pools/RSETHPoolV2.sol (L285-299)
```text
    /// @dev Withdraws assets from the L2 to L1
    function bridgeAssets() external nonReentrant onlyRole(BRIDGER_ROLE) {
        UtilLib.checkNonZeroAddress(l2Bridge);
        UtilLib.checkNonZeroAddress(messenger);
        UtilLib.checkNonZeroAddress(l1VaultETHForL2Chain);

        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
    }
```
