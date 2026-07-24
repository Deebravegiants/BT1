### Title
Fee-on-Transfer Token Accounting Discrepancy in `initTransfer` Breaks EVM-to-NEAR Backing Guarantee — (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`OmniBridge.initTransfer` locks native ERC20 tokens by calling `safeTransferFrom(msg.sender, address(this), amount)` and then unconditionally emits `InitTransfer` with the caller-supplied `amount`. For fee-on-transfer tokens the bridge receives fewer tokens than `amount`, yet the NEAR side mints the full `amount` to the recipient, permanently undercollateralizing the bridge vault.

---

### Finding Description

In the `else` branch of `initTransfer` (the path for plain ERC20 tokens that are neither bridge-deployed nor custom-minted), the contract transfers tokens and immediately emits the event using the raw parameter:

```solidity
// OmniBridge.sol lines 407-411
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount          // ← actual received may be less for fee-on-transfer tokens
);
```

```solidity
// OmniBridge.sol lines 427-436
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,         // ← always the parameter, never the actual balance delta
    fee,
    nativeFee,
    recipient,
    message
);
```

The NEAR prover decodes the event verbatim:

```rust
// near/omni-types/src/evm/events.rs line 126
amount: near_sdk::json_types::U128(event.data.amount),
```

`fin_transfer_callback` then builds the `TransferMessage` from that decoded amount:

```rust
// near/omni-bridge/src/lib.rs line 729
amount: Self::denormalize_amount(init_transfer.amount.0, decimals).into(),
```

And `process_fin_transfer_to_near` releases `amount_without_fee` tokens to the recipient:

```rust
// near/omni-bridge/src/lib.rs lines 1962-1971
self.send_tokens(
    token.clone(),
    recipient,
    U128(transfer_message.amount_without_fee()...),
    &msg,
)
```

Because the NEAR side trusts the event's `amount` field entirely, any shortfall between the emitted amount and the actual tokens received on EVM is silently absorbed as unbacked supply on NEAR.

---

### Impact Explanation

**Critical / High — backing guarantee violation.**

For every `initTransfer` call involving a fee-on-transfer token:

- EVM vault receives `amount − transfer_fee` tokens.
- NEAR mints `amount` tokens to the recipient.
- The vault is permanently short by `transfer_fee` per transfer.

Accumulated shortfalls mean that when later users attempt to bridge back, the EVM vault will not hold enough tokens to honour all outstanding NEAR-side claims. The last redeemers face an irreversible fund lock / permanently unclaimable value — squarely within the allowed impact scope ("asset-identity / balance-accounting divergence that breaks backing guarantees").

---

### Likelihood Explanation

**Medium.** The token must be registered on the NEAR side (admin sets `token_decimals`), which is a prerequisite. However:

1. Admins may register tokens without auditing their transfer implementation.
2. Some tokens add or modify transfer fees after deployment (upgradeable proxies).
3. Once a fee-on-transfer token is registered, **any unprivileged user** can call `initTransfer` and profit: they receive the full `amount` on NEAR while the vault is shorted by the fee. There is no front-running required and no special knowledge needed beyond knowing the token charges a fee.

---

### Recommendation

Measure the actual balance delta around the `safeTransferFrom` call and use that value in the event emission, mirroring the fix applied in the referenced Solidly commit:

```solidity
} else {
    uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
    IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
    uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
    require(actualReceived > fee, "InvalidFee");
    amount = uint128(actualReceived); // use actual for event and downstream logic
}
```

Emit and pass `amount` (now the actual received value) to `initTransferExtension` and the `InitTransfer` event so the NEAR side mints exactly what was locked.

---

### Proof of Concept

1. Admin registers a fee-on-transfer ERC20 token `FoT` (1 % transfer fee) on both EVM and NEAR sides.
2. Alice calls `OmniBridge.initTransfer(FoT, 1_000_000, 0, 0, "near:alice.near", "")`.
3. `safeTransferFrom` moves 1 000 000 tokens from Alice; the token contract deducts 1 % → vault receives **990 000**.
4. `InitTransfer` event is emitted with `amount = 1_000_000`.
5. Relayer submits proof to NEAR `fin_transfer`; `fin_transfer_callback` decodes `amount = 1_000_000` and mints **1 000 000** wrapped `FoT` to `alice.near`.
6. Vault holds 990 000 tokens but NEAR has 1 000 000 outstanding claims — a 10 000-token shortfall per call.
7. Repeated calls drain the backing ratio; the last redeemers cannot withdraw their tokens from the EVM vault.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L427-436)
```text
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

**File:** near/omni-types/src/evm/events.rs (L115-136)
```rust
impl TryFromLog<Log<InitTransfer>> for InitTransferMessage {
    type Error = String;

    fn try_from_log(chain_kind: ChainKind, event: Log<InitTransfer>) -> Result<Self, Self::Error> {
        Ok(Self {
            emitter_address: OmniAddress::new_from_evm_address(
                chain_kind,
                H160(event.address.into()),
            )?,
            origin_nonce: event.data.originNonce,
            token: OmniAddress::new_from_evm_address(chain_kind, H160(event.tokenAddress.into()))?,
            amount: near_sdk::json_types::U128(event.data.amount),
            recipient: event.data.recipient.parse().map_err(stringify)?,
            fee: Fee {
                fee: near_sdk::json_types::U128(event.data.fee),
                native_fee: near_sdk::json_types::U128(event.data.nativeTokenFee),
            },
            sender: OmniAddress::new_from_evm_address(chain_kind, H160(event.data.sender.into()))?,
            msg: event.data.message,
        })
    }
}
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

**File:** near/omni-bridge/src/lib.rs (L1962-1971)
```rust
        self.send_tokens(
            token.clone(),
            recipient,
            U128(
                transfer_message
                    .amount_without_fee()
                    .near_expect(BridgeError::InvalidFee),
            ),
            &msg,
        )
```
