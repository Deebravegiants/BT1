### Title
Missing Zero-Amount Guard in `bridgeAssetsViaNativeBridge` Allows Silent No-Op Bridge Call — (`contracts/pools/RSETHPool.sol`)

### Summary
`RSETHPool.bridgeAssetsViaNativeBridge()` does not check that `getETHBalanceMinusFees()` is nonzero before forwarding the value to the messenger. When `feeEarnedInETH == address(this).balance`, the function calls `sendETHToL1ViaBridge{value: 0}(...)`, which in turn calls `IArbitrumMessenger(l2bridge).withdrawEth{value: 0}(target)`. If the Arbitrum bridge precompile does not revert on a zero-value call, the entire sequence completes without reverting and emits `BridgedETHToL1ViaNativeBridge` with `amount=0`, falsely signalling a successful bridge operation.

### Finding Description

`bridgeAssetsViaNativeBridge` computes `ethBalanceMinusFees` and passes it directly to the messenger with no zero-value guard: [1](#0-0) 

```solidity
function bridgeAssetsViaNativeBridge() external nonReentrant onlyRole(BRIDGER_ROLE) {
    ...
    uint256 ethBalanceMinusFees = getETHBalanceMinusFees();   // can be 0

    IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
        l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees   // value: 0, amount: 0
    );

    emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees); // amount=0
}
```

`getETHBalanceMinusFees()` returns `address(this).balance - feeEarnedInETH`, which is exactly `0` whenever all ETH in the pool is accumulated fees: [2](#0-1) 

Inside `ArbitrumMessenger.sendETHToL1ViaBridge`, the only guard is `msg.value != value`. When both are `0`, this check passes: [3](#0-2) 

The call then reaches `IArbitrumMessenger(l2bridge).withdrawEth{value: 0}(target)`. The interface imposes no revert requirement on zero value: [4](#0-3) 

Contrast this with `bridgeTokens`, which explicitly guards against zero balance: [5](#0-4) 

And `moveAssetsForBridging`, which reverts on zero amount: [6](#0-5) 

`bridgeAssetsViaNativeBridge` is the only bridging path that lacks this guard.

### Impact Explanation
L1Vault receives no ETH while the L2 pool emits `BridgedETHToL1ViaNativeBridge` with `amount=0`. No principal is lost, but the function fails to deliver its promised return (bridging ETH to L1) and produces a misleading success event. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation
The state `feeEarnedInETH == address(this).balance` is reachable through normal operation: after all principal ETH has been bridged via `moveAssetsForBridging` or `bridgeAssets`, only accumulated fees remain in the contract. A `BRIDGER_ROLE` caller invoking `bridgeAssetsViaNativeBridge` at that point (e.g., as part of a routine bridging script) would trigger the silent no-op. No malicious intent is required.

### Recommendation
Add a zero-amount check at the top of `bridgeAssetsViaNativeBridge`, consistent with the pattern used in `bridgeTokens` and `moveAssetsForBridging`:

```solidity
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
if (ethBalanceMinusFees == 0) revert ZeroBridgeAmount();
```

### Proof of Concept

1. Deploy `RSETHPool` with a mock `ArbitrumMessenger` and a mock Arbitrum bridge that does **not** revert on `withdrawEth{value: 0}`.
2. Simulate deposits so that `feeEarnedInETH` accumulates to equal `address(this).balance` (e.g., bridge all principal out first via `moveAssetsForBridging`, leaving only fees).
3. Call `bridgeAssetsViaNativeBridge()` as `BRIDGER_ROLE`.
4. Assert: no revert occurred, mock bridge received `0` ETH, `BridgedETHToL1ViaNativeBridge` was emitted with `ethBalanceMinusFees = 0`.

### Citations

**File:** contracts/pools/RSETHPool.sol (L387-389)
```text
    function getETHBalanceMinusFees() public view returns (uint256) {
        return address(this).balance - feeEarnedInETH;
    }
```

**File:** contracts/pools/RSETHPool.sol (L447-447)
```text
        if (amount == 0) revert InvalidAmount();
```

**File:** contracts/pools/RSETHPool.sol (L481-493)
```text
    function bridgeAssetsViaNativeBridge() external nonReentrant onlyRole(BRIDGER_ROLE) {
        UtilLib.checkNonZeroAddress(l2Bridge);
        UtilLib.checkNonZeroAddress(messenger);
        UtilLib.checkNonZeroAddress(l1VaultETHForL2Chain);

        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/pools/RSETHPool.sol (L556-560)
```text
        uint256 balance = getTokenBalanceMinusFees(token);

        if (balance == 0) {
            revert ZeroBridgeAmount();
        }
```

**File:** contracts/bridges/ArbitrumMessenger.sol (L21-24)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
    }
```

**File:** contracts/interfaces/L2/IArbitrumMessenger.sol (L13-13)
```text
    function withdrawEth(address destination) external payable;
```
