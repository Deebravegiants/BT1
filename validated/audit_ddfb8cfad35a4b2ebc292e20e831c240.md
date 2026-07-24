### Title
Fee-on-Transfer Token Accounting Divergence Creates Unbacked Cross-Chain Supply — (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary
`OmniBridge.initTransfer()` records the caller-supplied `amount` in the cross-chain message rather than the actual tokens received by the contract. For fee-on-transfer ERC20 tokens, the bridge locks fewer tokens than it attests to, causing the NEAR side to mint or release more tokens than are backed on the EVM side.

### Finding Description
In `OmniBridge.initTransfer()`, the native-token lock path calls `safeTransferFrom` with the user-supplied `amount`, then passes that same `amount` directly to `initTransferExtension` and the `InitTransfer` event without measuring the actual post-transfer balance: [1](#0-0) 

```solidity
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount          // ← user-supplied; actual receipt may be amount − fee
);
```

The unverified `amount` is then forwarded verbatim: [2](#0-1) 

For fee-on-transfer tokens the contract receives `amount − transferFee`, but the cross-chain message carries `amount`. The NEAR bridge's `fin_transfer_callback` deserialises `init_transfer.amount` directly from that proof and constructs the `TransferMessage` with the inflated figure: [3](#0-2) 

The NEAR side then mints or releases the full `amount` to the recipient, while the EVM vault only holds `amount − transferFee`.

### Impact Explanation
Every bridging call with a fee-on-transfer token creates a shortfall equal to the transfer fee. Over many transfers the EVM vault becomes progressively under-collateralised. Redemptions by later users will fail because the vault cannot cover the full minted supply — a permanent, irreversible backing shortfall. This matches the **High** impact category: *asset-accounting divergence that breaks backing guarantees*.

### Likelihood Explanation
`logMetadata` is a permissionless public function; any caller can register any ERC20 token. Fee-on-transfer tokens are common in production (e.g., tokens with reflection mechanics, USDT's dormant fee switch). Once a fee-on-transfer token is registered, every ordinary `initTransfer` call by any user silently inflates the minted supply. No privileged access or key compromise is required.

### Recommendation
Measure the actual received amount by comparing the vault balance before and after the `safeTransferFrom` call, and use that delta — not the caller-supplied `amount` — in the cross-chain message and event:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 received = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// use `received` (cast to uint128) instead of `amount` below
```

### Proof of Concept
1. Deploy a standard ERC20 with a 1 % transfer fee.
2. Call `logMetadata(tokenAddress)` on `OmniBridge` — permissionless, no role required.
3. Wait for the NEAR bridge to process the metadata and register the token.
4. Call `initTransfer(tokenAddress, 1_000_000, 0, 0, "near:alice.near", "")`.
   - `safeTransferFrom` moves 1 000 000 tokens from the caller; the contract receives 990 000.
   - `initTransferExtension` publishes a message with `amount = 1 000 000`.
5. The NEAR bridge verifies the proof and mints **1 000 000** tokens to `alice.near`.
6. The EVM vault holds only **990 000** tokens — 10 000 tokens of unbacked supply exist.
7. Repeat to widen the shortfall until redemptions revert for lack of funds.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L406-412)
```text
            } else {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
            }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L415-425)
```text
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

**File:** near/omni-bridge/src/lib.rs (L726-736)
```rust
        let transfer_message = TransferMessage {
            origin_nonce: init_transfer.origin_nonce,
            token: init_transfer.token,
            amount: Self::denormalize_amount(init_transfer.amount.0, decimals).into(),
            recipient: init_transfer.recipient,
            fee: Self::denormalize_fee(&init_transfer.fee, decimals),
            sender: init_transfer.sender,
            msg: init_transfer.msg,
            destination_nonce,
            origin_transfer_id: None,
        };
```
