### Title
Fee-on-Transfer Token Accounting Divergence in `initTransfer` Breaks Bridge Backing Guarantees — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary

`OmniBridge.initTransfer` uses the caller-supplied `amount` parameter in the emitted `InitTransfer` event without verifying that the contract actually received that amount. For fee-on-transfer ERC20 tokens, the bridge receives `amount - transferFee` tokens but the event records `amount`. The NEAR side treats the event as the sole source of truth and credits the full `amount` to the recipient, permanently underbacking the bridge's locked-token reserve.

### Finding Description

In `OmniBridge.initTransfer`, the non-bridge, non-custom ERC20 lock path is:

```solidity
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount          // ← requested amount, not actual received
);
```

followed immediately by:

```solidity
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,         // ← same caller-supplied value, not balance delta
    fee,
    nativeFee,
    recipient,
    message
);
``` [1](#0-0) 

No balance-before/balance-after check is performed. For a fee-on-transfer ERC20, `safeTransferFrom` succeeds (the token's `transferFrom` returns `true`) but the contract receives only `amount - transferFee`. The event still records the full `amount`.

The NEAR side is explicitly designed to treat the emitted event as the only authoritative record of the transfer:

> "The NEAR side reads this event (via light client or Wormhole) to complete the transfer. Every field needed to reconstruct the transfer must be in the event — it is the only data the NEAR side sees." [2](#0-1) 

The NEAR prover parses the `InitTransfer` event's `amount` field directly from the EVM log: [3](#0-2) 

The same structural flaw exists in the Starknet bridge, which calls `transfer_from(caller, get_contract_address(), amount.into())` and then emits `amount` in the event without a balance delta check: [4](#0-3) 

### Impact Explanation

Each `initTransfer` call with a fee-on-transfer token creates a permanent deficit: the EVM bridge holds `amount - transferFee` tokens but the NEAR side has credited `amount` tokens to the recipient. Over multiple transfers the cumulative shortfall grows. When users later bridge tokens back from NEAR to EVM, the bridge will be unable to release the full amount to some users — either reverting their withdrawals or draining the reserves of honest depositors. This is a direct backing-guarantee violation: the bridge's locked ERC20 balance no longer covers the outstanding NEAR-side supply.

This falls squarely under: **"Asset-identity, token-mapping, decimals, fee-routing, refund, or balance-accounting divergence that breaks backing guarantees or sends value to the wrong party."**

### Likelihood Explanation

The bridge imposes no whitelist on which ERC20 tokens can be passed to `initTransfer` — any address that is not in `isBridgeToken` and not in `customMinters` takes the vulnerable lock path. Fee-on-transfer tokens (e.g. STA, PAXG, tokens with configurable fees) are common on mainnet. A single user calling `initTransfer` with such a token is sufficient to trigger the discrepancy; no coordination or privileged access is required.

### Recommendation

Replace the fixed-`amount` accounting with a balance-delta pattern for the ERC20 lock path:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
require(actualReceived == amount, "fee-on-transfer token not supported");
```

Either enforce that only standard (non-fee) tokens are accepted (revert on discrepancy), or emit `actualReceived` in the event instead of `amount`. Apply the same fix to the Starknet `init_transfer` and audit the Solana Token-2022 path for the transfer-fee extension.

### Proof of Concept

1. Deploy a standard ERC20 with a 1% transfer fee (or use an existing one such as STA).
2. Register the token on the NEAR side so the bridge accepts it.
3. Call `OmniBridge.initTransfer(feeToken, 1000, 0, 0, "alice.near", "")` after approving 1000 tokens.
4. `safeTransferFrom` succeeds; bridge receives 990 tokens (1% fee deducted).
5. `InitTransfer` event is emitted with `amount = 1000`.
6. NEAR prover reads the event; NEAR bridge credits 1000 tokens to `alice.near`.
7. Bridge EVM balance: 990. NEAR-side outstanding: 1000. Deficit: 10 per call.
8. Repeat N times; deficit grows to `N × 10`. The Nth honest user bridging back cannot withdraw their full amount. [5](#0-4) [6](#0-5)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L406-436)
```text
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
```

**File:** evm/CLAUDE.md (L23-23)
```markdown
**EVM → NEAR (initTransfer)**: User calls `initTransfer` which burns/locks tokens on EVM and emits `InitTransfer` with all transfer details (sender, token, amount, fee, nativeFee, recipient, message). In the Wormhole variant, a Wormhole message is also sent. The NEAR side reads this event (via light client or Wormhole) to complete the transfer. Every field needed to reconstruct the transfer must be in the event — it is the only data the NEAR side sees.
```

**File:** near/omni-types/src/evm/events.rs (L12-21)
```rust
    event InitTransfer(
        address indexed sender,
        address indexed tokenAddress,
        uint64 indexed originNonce,
        uint128 amount,
        uint128 fee,
        uint128 nativeTokenFee,
        string recipient,
        string message
    );
```

**File:** starknet/src/omni_bridge.cairo (L303-330)
```text
            } else {
                let success = IERC20Dispatcher { contract_address: token_address }
                    .transfer_from(caller, get_contract_address(), amount.into());
                assert(success, 'ERR_TRANSFER_FROM_FAILED');
            }

            if native_fee > 0 {
                let native_token = self.strk_token_address.read();
                let success = IERC20Dispatcher { contract_address: native_token }
                    .transfer_from(caller, get_contract_address(), native_fee.into());
                assert(success, 'ERR_FEE_TRANSFER_FAILED');
            }

            self
                .emit(
                    Event::InitTransfer(
                        InitTransfer {
                            sender: caller,
                            token_address,
                            origin_nonce,
                            amount,
                            fee,
                            native_fee,
                            recipient,
                            message,
                        },
                    ),
                )
```
