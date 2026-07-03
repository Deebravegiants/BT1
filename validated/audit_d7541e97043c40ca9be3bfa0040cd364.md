### Title
Exact `msg.value` Equality Check in `bridgeTokenToL1` Causes Revert on LayerZero Fee Fluctuation - (File: contracts/bridges/TACWETHBridge.sol)

### Summary
`TACWETHBridge.bridgeTokenToL1()` computes the LayerZero native fee internally via `getNativeFee()` and then enforces `msg.value != nativeFee` with a strict equality revert. Because LayerZero fees are dynamic (driven by destination-chain gas prices and asset conversion rates), any fee change between the user's off-chain quote call and on-chain execution causes the transaction to revert, permanently blocking the bridge attempt until the user retries with a freshly-quoted value that may itself be stale by execution time.

### Finding Description
`TACWETHBridge.bridgeTokenToL1()` is a publicly callable, permissionless function (no role restriction) that bridges WETH from TAC to Ethereum L1 via LayerZero OFT.

```solidity
// contracts/bridges/TACWETHBridge.sol
function bridgeTokenToL1(address recipient, uint256 amount) external payable nonReentrant {
    ...
    uint256 nativeFee = getNativeFee(amount, recipient);   // queries wethOFT.quoteSend() on-chain

    if (msg.value != nativeFee) {                          // strict equality
        revert InvalidNativeFee();
    }
    ...
    MessagingFee memory fee = MessagingFee({ nativeFee: nativeFee, lzTokenFee: 0 });
    (, OFTReceipt memory oftReceipt) = wethOFT.send{ value: nativeFee }(sendParam, fee, msg.sender);
}
``` [1](#0-0) 

`getNativeFee()` calls `wethOFT.quoteSend(sendParam, false)`, which returns a fee that depends on the current gas price on Ethereum mainnet and LayerZero's asset conversion rates — both of which fluctuate continuously. [2](#0-1) 

The standard user flow is:
1. Call `getNativeFee(amount, recipient)` off-chain to determine how much ETH to attach.
2. Submit `bridgeTokenToL1(recipient, amount)` with `msg.value = quotedFee`.
3. Inside the function, `getNativeFee()` is called **again** at execution time.
4. If the fee increased by even 1 wei between steps 1 and 3, `msg.value != nativeFee` and the transaction reverts with `InvalidNativeFee`.

There is no excess-refund path and no `>=` tolerance. The function accepts only the exact fee computed at the moment of execution, which the caller cannot know in advance with certainty.

### Impact Explanation
Any user on TAC attempting to bridge WETH to L1 faces repeated transaction reverts whenever Ethereum mainnet gas prices move between quote and execution. Because the function is permissionless and the fee is re-derived inside the call, there is no window in which the user can guarantee success during periods of fee volatility. This constitutes a **temporary freezing of user funds** — WETH is not lost, but users are unable to bridge it to L1 for the duration of the volatility window.

**Impact: Medium — Temporary freezing of funds.**

### Likelihood Explanation
LayerZero fees are driven by destination-chain gas prices and oracle-reported asset conversion rates, both of which change on every block during normal Ethereum operation. Any period of moderate network activity (e.g., NFT mint, airdrop, market event) is sufficient to cause the fee to shift between the user's off-chain quote and on-chain execution. No attacker action is required; this is a routine occurrence. Likelihood is **High**.

### Recommendation
Replace the strict equality check with a minimum-fee check and refund any excess `msg.value` to the caller:

```solidity
uint256 nativeFee = getNativeFee(amount, recipient);
if (msg.value < nativeFee) {
    revert InvalidNativeFee();
}
// use nativeFee for the send, refund surplus
uint256 surplus = msg.value - nativeFee;
MessagingFee memory fee = MessagingFee({ nativeFee: nativeFee, lzTokenFee: 0 });
(, OFTReceipt memory oftReceipt) = wethOFT.send{ value: nativeFee }(sendParam, fee, msg.sender);
if (surplus > 0) {
    (bool ok,) = payable(msg.sender).call{ value: surplus }("");
    require(ok, "refund failed");
}
```

This mirrors the fix applied in the referenced Securitize report and is the standard pattern used by LayerZero integrations.

### Proof of Concept
1. User calls `TACWETHBridge.getNativeFee(1 ether, recipientAddress)` off-chain → returns `fee = 0.001 ether`.
2. Ethereum mainnet gas price spikes; LayerZero's oracle updates the fee to `0.0010001 ether`.
3. User submits `bridgeTokenToL1{value: 0.001 ether}(recipientAddress, 1 ether)`.
4. Inside the function, `getNativeFee()` now returns `0.0010001 ether`.
5. `msg.value (0.001 ether) != nativeFee (0.0010001 ether)` → `revert InvalidNativeFee()`.
6. User's WETH remains on TAC; they cannot bridge until they retry with a new quote that may itself be stale. [3](#0-2) [4](#0-3)

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
