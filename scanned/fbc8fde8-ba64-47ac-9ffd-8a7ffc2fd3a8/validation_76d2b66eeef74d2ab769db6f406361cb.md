### Title
`bridgeTokens` Forwards `msg.value` to `ArbitrumLidoBridge` Which Unconditionally Reverts on Any ETH — ([File: contracts/bridges/ArbitrumLidoBridge.sol])

### Summary

`RSETHPoolV3ExternalBridge.bridgeTokens` is `payable` and explicitly designed to forward `msg.value` to the underlying bridge for fee payment. However, `ArbitrumLidoBridge.bridgeTokenToL1` unconditionally reverts with `NoMsgValueNeeded` when any ETH is attached. Any `BRIDGER_ROLE` call to `bridgeTokens(wstETH)` with `msg.value > 0` will always revert, making the function fail to deliver its documented behavior for the wstETH/Arbitrum path.

### Finding Description

`RSETHPoolV3ExternalBridge.bridgeTokens` is declared `payable` and carries an explicit comment at line 735–736:

> *"msg.value is included in case we need to pay for additional bridging fees"*

It unconditionally forwards whatever ETH the caller sends:

```solidity
IL2TokenBridge(tokenBridge[token]).bridgeTokenToL1{ value: msg.value }(l1VaultETHForL2Chain, balance);
``` [1](#0-0) 

`ArbitrumLidoBridge.bridgeTokenToL1`, however, hard-rejects any non-zero `msg.value` at the very top of its body:

```solidity
if (msg.value != 0) {
    revert NoMsgValueNeeded();
}
``` [2](#0-1) 

The two contracts have directly contradictory assumptions: the pool is designed to pass ETH for fees; the bridge is designed to refuse ETH entirely. A `BRIDGER_ROLE` caller who follows the pool's documented interface and supplies any ETH will always receive a revert.

### Impact Explanation

The impact is **Low — contract fails to deliver promised returns, but doesn't lose value**.

- `bridgeTokens` is `payable` and its inline comment promises that `msg.value` will be forwarded for bridging fees. For the wstETH/`ArbitrumLidoBridge` path this promise is broken: any non-zero `msg.value` causes an unconditional revert.
- The wstETH balance in the pool is **not permanently frozen**: a subsequent call with `msg.value = 0` succeeds normally. The blocking is conditional, not permanent.
- No funds are lost; the revert unwinds all state changes.

### Likelihood Explanation

Likelihood is **Low**. The `BRIDGER_ROLE` is a trusted, permissioned role. The revert only occurs when the caller explicitly attaches ETH. A caller who reads `ArbitrumLidoBridge`'s NatSpec (which states "No additional msg.value is needed for the fees") will call with `msg.value = 0` and succeed. The inconsistency is a documentation/interface mismatch rather than an exploitable attack vector. [3](#0-2) 

### Recommendation

Two complementary fixes:

1. **In `RSETHPoolV3ExternalBridge.bridgeTokens`**: Before forwarding, check whether the target bridge accepts ETH. Alternatively, only forward `msg.value` when the bridge is known to require it (e.g., a Stargate/LayerZero bridge), and revert early with a descriptive error if `msg.value > 0` is supplied for a bridge that does not accept ETH. [4](#0-3) 

2. **In `ArbitrumLidoBridge.bridgeTokenToL1`**: The function is declared `payable` in the `IL2TokenBridge` interface, which is what allows the pool to call it with `{value: msg.value}`. If the Arbitrum Lido bridge never needs ETH, the interface and implementation should be made non-`payable`, or the pool should guard against forwarding ETH to it. [5](#0-4) 

### Proof of Concept

```solidity
// Fork test on Arbitrum
function test_bridgeTokens_revertsWithMsgValue() external {
    // Preconditions: pool has wstETH balance > feeBps, tokenBridge[wstETH] = ArbitrumLidoBridge
    uint256 balanceBefore = IERC20(wstETH).balanceOf(address(pool));

    vm.prank(bridgerRole);
    vm.expectRevert(ArbitrumLidoBridge.NoMsgValueNeeded.selector);
    pool.bridgeTokens{value: 1 wei}(wstETH);

    // wstETH balance unchanged — tokens not bridged
    assertEq(IERC20(wstETH).balanceOf(address(pool)), balanceBefore);

    // Calling with msg.value == 0 succeeds
    vm.prank(bridgerRole);
    pool.bridgeTokens{value: 0}(wstETH); // succeeds
}
```

### Citations

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L715-740)
```text
    function bridgeTokens(address token)
        external
        payable
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        if (tokenBridge[token] == address(0)) {
            revert MissingBridgeForToken();
        }

        uint256 balance = getTokenBalanceMinusFees(token);

        if (balance == 0) {
            revert ZeroBridgeAmount();
        }

        // Approve the required amount to the bridge
        IERC20(token).safeIncreaseAllowance(tokenBridge[token], balance);

        // Call the bridge contract to transfer the tokens (msg.value is included in case we need to pay for additional
        // bridging fees)
        IL2TokenBridge(tokenBridge[token]).bridgeTokenToL1{ value: msg.value }(l1VaultETHForL2Chain, balance);

        emit BridgedTokenToL1(token, l1VaultETHForL2Chain, balance);
    }
```

**File:** contracts/bridges/ArbitrumLidoBridge.sol (L54-57)
```text
    /**
     * @notice Bridges wstETH from Arbitrum to L1
     * @dev No additional msg.value is needed for the fees, hence we reject it to
     *      avoid having stuck ETH in the contract
```

**File:** contracts/bridges/ArbitrumLidoBridge.sol (L61-71)
```text
    function bridgeTokenToL1(address recipient, uint256 amount) external payable nonReentrant {
        UtilLib.checkNonZeroAddress(recipient);

        if (amount == 0) {
            revert ZeroAmount();
        }

        // No additional msg.value is needed for the fees
        if (msg.value != 0) {
            revert NoMsgValueNeeded();
        }
```
