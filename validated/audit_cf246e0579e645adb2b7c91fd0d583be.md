### Title
Strict `msg.value` Equality Check Against a Dynamically-Computed LayerZero Fee Causes Denial of Service on Bridging — (File: `contracts/bridges/TACWETHBridge.sol`)

---

### Summary

`TACWETHBridge.bridgeTokenToL1` computes the LayerZero native fee **at execution time** via `wethOFT.quoteSend()` and then enforces `msg.value != nativeFee` with strict equality. Because LayerZero fees are dynamic and can shift between the block in which a user queries the fee and the block in which the transaction is mined, any discrepancy — even 1 wei — causes an `InvalidNativeFee` revert, permanently blocking the bridging call until a perfectly-timed retry succeeds.

---

### Finding Description

In `TACWETHBridge.bridgeTokenToL1`:

```solidity
uint256 nativeFee = getNativeFee(amount, recipient);   // queries wethOFT.quoteSend() on-chain
if (msg.value != nativeFee) {                          // strict equality
    revert InvalidNativeFee();
}
``` [1](#0-0) 

`getNativeFee` internally calls `wethOFT.quoteSend(sendParam, false)`, whose return value is a live LayerZero oracle quote that changes with destination-chain gas prices: [2](#0-1) 

A caller must supply `msg.value` equal to the fee **as it will be computed inside the transaction**, not as it was when they queried it off-chain. Because the fee is re-derived at execution time, any change between query and mining causes a revert. The check uses `!=` (not `<`), so even sending *more* ETH than the fee also reverts.

The same strict-equality pattern appears in the pool-level `bridgeAssets` functions, but those are `BRIDGER_ROLE`-gated. `TACWETHBridge.bridgeTokenToL1` carries **no role restriction** and is directly callable by any user holding WETH: [3](#0-2) 

Additionally, the pool's `bridgeTokens` (BRIDGER_ROLE) forwards `msg.value` verbatim to `bridgeTokenToL1`, so the same fragility affects the privileged bridging path: [4](#0-3) 

---

### Impact Explanation

When the LayerZero fee shifts between query and execution, `bridgeTokenToL1` reverts. For the direct-user path, the user's WETH is never transferred (the check precedes the `safeTransferFrom`), so no funds are lost — but the bridge call is blocked. For the `bridgeTokens` path, tokens collected in the pool cannot be moved to L1 until a perfectly-timed call succeeds, constituting **temporary freezing of funds** held in the pool.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

LayerZero native fees fluctuate with destination-chain gas prices, which change every block. During periods of gas price volatility (common on Ethereum mainnet), the fee returned by `quoteSend` at query time and at execution time will routinely differ. The strict `!=` check means even a 1-wei difference causes a revert. This is a realistic, recurring condition in normal operation, not a theoretical edge case.

---

### Recommendation

Replace the strict equality check with a lower-bound check and refund any excess:

```solidity
if (msg.value < nativeFee) {
    revert InvalidNativeFee();
}
uint256 excess = msg.value - nativeFee;
if (excess > 0) {
    (bool ok,) = payable(msg.sender).call{value: excess}("");
    require(ok, "refund failed");
}
```

This mirrors the standard pattern used by LayerZero integrations and eliminates the race condition between fee quotation and transaction inclusion.

---

### Proof of Concept

1. User calls `getNativeFee(1e18, recipient)` off-chain at block N → returns `0.001 ETH`.
2. User submits `bridgeTokenToL1(recipient, 1e18)` with `msg.value = 0.001 ETH`.
3. Between block N and block N+2, Ethereum mainnet gas spikes; LayerZero fee rises to `0.0011 ETH`.
4. At execution, `getNativeFee` re-queries `wethOFT.quoteSend()` → `nativeFee = 0.0011 ETH`.
5. `msg.value (0.001 ETH) != nativeFee (0.0011 ETH)` → `revert InvalidNativeFee()`.
6. Transaction reverts; WETH is never transferred; bridging is blocked until a retry lands in a block where the fee happens to match exactly. [1](#0-0)

### Citations

**File:** contracts/bridges/TACWETHBridge.sol (L100-113)
```text
    function bridgeTokenToL1(address recipient, uint256 amount) external payable nonReentrant {
        UtilLib.checkNonZeroAddress(recipient);

        if (amount == 0) {
            revert ZeroAmount();
        }

        // Calculate the native fee for bridging
        uint256 nativeFee = getNativeFee(amount, recipient);

        // Check if the msg.value is equal to the native fee for bridging
        if (msg.value != nativeFee) {
            revert InvalidNativeFee();
        }
```

**File:** contracts/bridges/TACWETHBridge.sol (L142-162)
```text
    function getNativeFee(uint256 amount, address receiver) public view returns (uint256) {
        UtilLib.checkNonZeroAddress(receiver);

        if (amount == 0) {
            revert ZeroAmount();
        }

        SendParam memory sendParam = SendParam({
            dstEid: dstLzChainId,
            to: getReceiver(receiver),
            amountLD: amount,
            minAmountLD: getMinAmount(amount),
            extraOptions: bytes(""),
            composeMsg: bytes(""),
            oftCmd: bytes("")
        });

        MessagingFee memory fee = wethOFT.quoteSend(sendParam, false);

        return fee.nativeFee;
    }
```

**File:** contracts/pools/RSETHPool.sol (L563-568)
```text
        IERC20(token).safeIncreaseAllowance(tokenBridge[token], balance);

        // Call the bridge contract to transfer the tokens (msg.value is included in case we need to pay for additional
        // bridging fees)
        IL2TokenBridge(tokenBridge[token]).bridgeTokenToL1{ value: msg.value }(l1VaultETHForL2Chain, balance);

```
