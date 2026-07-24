### Title
Fee-on-Transfer Token Accounting Divergence in `initTransfer` Creates Unbacked Wrapped Supply — (`evm/src/omni-bridge/contracts/OmniBridge.sol`, `starknet/src/omni_bridge.cairo`)

### Summary
`OmniBridge.initTransfer` (EVM) and `init_transfer` (Starknet) record the caller-supplied `amount` in the `InitTransfer` event without verifying the actual tokens received. For fee-on-transfer ERC-20 tokens the bridge receives `amount − fee_taken` but the event asserts `amount`, causing the destination chain to mint or release the full `amount` against an undercollateralized reserve.

### Finding Description
In `OmniBridge.sol`, the non-bridge-token, non-custom-minter branch of `initTransfer` executes:

```solidity
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
```

and immediately emits:

```solidity
emit BridgeTypes.InitTransfer(msg.sender, tokenAddress, currentOriginNonce, amount, fee, nativeFee, recipient, message);
``` [1](#0-0) [2](#0-1) 

No balance snapshot is taken before the transfer, and no post-transfer balance check is performed. The emitted `amount` is the caller's input, not the actual credit to the bridge.

The identical pattern exists in Starknet's `init_transfer`:

```cairo
let success = IERC20Dispatcher { contract_address: token_address }
    .transfer_from(caller, get_contract_address(), amount.into());
assert(success, 'ERR_TRANSFER_FROM_FAILED');
// ...
emit Event::InitTransfer(InitTransfer { ..., amount, ... })
``` [3](#0-2) [4](#0-3) 

### Impact Explanation
The `InitTransfer` event is the proof payload consumed by the destination chain (NEAR or another EVM/Starknet chain) to mint or release wrapped tokens. When the event records `amount` but the bridge only holds `amount − transfer_fee`, every such transfer creates a shortfall in the locked reserve. After N transfers the bridge is undercollateralized by `N × transfer_fee` tokens. Redemptions on the destination chain will eventually fail because the bridge cannot cover all outstanding wrapped supply — a permanent, irreversible backing guarantee violation. This matches the allowed impact: *"Asset-identity, token-mapping, decimals, fee-routing, refund, or balance-accounting divergence that breaks backing guarantees."*

### Likelihood Explanation
USDT (Ethereum mainnet) has a fee mechanism that is currently set to zero but can be activated by its owner at any time. Any token with a configurable transfer fee that is later enabled, or any token that already charges fees, triggers this path. The attacker path is fully unprivileged: any user calling `initTransfer` with such a token causes the divergence. No special role or key is required.

### Recommendation
Measure the actual received amount using a balance snapshot pattern:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// Use actualReceived (cast to uint128 with overflow check) in the event and downstream logic
```

Apply the same fix to Starknet's `init_transfer`. Alternatively, maintain an explicit allowlist of supported tokens and reject any token whose post-transfer balance does not match the declared amount.

### Proof of Concept
1. Deploy or use a fee-on-transfer ERC-20 token (e.g., 1% fee) on an EVM chain where `OmniBridge` is deployed.
2. Approve the bridge for `1000` tokens and call `initTransfer(tokenAddress, 1000, 0, 0, "recipient.near", "")`.
3. The bridge receives `990` tokens (`safeTransferFrom` deducts 1% fee), but emits `InitTransfer(..., amount=1000, ...)`.
4. The NEAR bridge processes the proof from this event and mints `1000` wrapped tokens to the recipient.
5. The EVM bridge now holds only `990` tokens backing `1000` wrapped tokens — a `10`-token shortfall per transfer.
6. Repeat to drain the reserve; eventually legitimate redemptions (`finTransfer` back to EVM) will fail because the bridge cannot transfer the full `amount` to redeeming users.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L407-411)
```text
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
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

**File:** starknet/src/omni_bridge.cairo (L304-306)
```text
                let success = IERC20Dispatcher { contract_address: token_address }
                    .transfer_from(caller, get_contract_address(), amount.into());
                assert(success, 'ERR_TRANSFER_FROM_FAILED');
```

**File:** starknet/src/omni_bridge.cairo (L316-330)
```text
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
