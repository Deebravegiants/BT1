Confirmed: `WrappedHyperFungibleToken.send()` locks the underlying token via a raw `safeTransferFrom` without verifying the actual amount received, unlike `IntentGatewayV2.placeOrder()` in the same repo, which explicitly guards against this by measuring `balanceOf` before/after every transfer. [1](#0-0) [2](#0-1) 

### Title
Unbacked cross-chain mint/unlock from fee-on-transfer or rebasing underlying tokens in `WrappedHyperFungibleToken.send` - ([File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken.send()` pulls `params.amount` of the underlying ERC20 via `safeTransferFrom` and encodes that same `params.amount` into the cross-chain `Message` body, without checking how much the contract actually received. If the underlying token charges a transfer fee or is a deflationary/rebasing token, the contract's actual locked balance is less than `params.amount`, but the destination chain still mints or unlocks the full, unbacked `params.amount`.

### Finding Description
In `send()`, the escrow branch does:
```solidity
IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
```
with no balance-before/balance-after check, then immediately builds the dispatch message using the original, unadjusted `params.amount`:
```solidity
bytes memory body = abi.encode(HyperFungibleToken.Message({
    from: abi.encodePacked(msg.sender),
    to: params.to,
    amount: params.amount,
    data: params.data
}));
``` [3](#0-2) 

The escrow model described in the contract's own docs and in `BridgeToken.sol` relies on the destination mint/unlock being fully backed by what is locked on this "home chain" side. [4](#0-3)  When the underlying token deducts a fee on transfer or rebases downward, this contract locks less than `params.amount` while the message still claims the full `params.amount` was locked. On the receiving side, either a peer `HyperFungibleToken` mints the full unbacked `message.amount` [5](#0-4) , or a peer `WrappedHyperFungibleToken` unlocks `message.amount` of its own underlying escrow via `safeTransfer` [6](#0-5) , draining more value than was actually deposited.

This is directly analogous to the `StakingRewards` bug class: an unprivileged caller (any token bridger) triggers a single `send()` transaction with a fee-on-transfer/rebasing underlying and the contract accounts for the nominal amount instead of the actually-received amount.

Notably, the same repo's `IntentGatewayV2.placeOrder()` already applies the correct fix pattern for this exact issue (see snapshot balances before/after transfer and mutate `order.inputs[i].amount` to the actual received amount) [7](#0-6) , but `WrappedHyperFungibleToken` was not updated with the equivalent guard.

### Impact Explanation
This breaks the fundamental backing invariant of the bridge: mints on burn/mint deployments become unbacked, and lock/unlock escrows on other deployments can be drained below their real balance, since every subsequent redemption assumes the nominal amount was actually escrowed. Over repeated transfers this is a systemic under-collateralization of the token supply — a critical asset-integrity failure reachable by any single unprivileged user simply calling `send()` with a fee-on-transfer or rebasing/deflationary ERC20 configured as the underlying.

### Likelihood Explanation
Likelihood depends on whether a fee-on-transfer/rebasing token is ever configured as `_underlying` for a `WrappedHyperFungibleToken` deployment. Since `configure()` is owner-controlled but does not enforce non-fee-on-transfer semantics, and the SDK/docs describe this contract as a general-purpose wrapper for "existing ERC20 tokens" [8](#0-7) , deploying it against such a token is a realistic operational scenario, and once deployed, exploitation requires only a normal `send()` call by any user — no privileged access needed.

### Recommendation
Mirror the fix already applied in `IntentGatewayV2.placeOrder()`: snapshot `IERC20(_underlying).balanceOf(address(this))` before the `safeTransferFrom` call in `send()`, compute the actual received delta afterward, and use that delta (not `params.amount`) both when constructing the dispatched `Message.amount` and in the emitted `Sent` event. Apply the analogous check to the WETH-deposit branch if the wrapped WETH implementation can ever deviate from a 1:1 mint.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` set to a token that deducts a 1% fee on transfer (or is deflationary/rebasing).
2. User calls `send({ amount: 1000e18, ... })`. The contract's actual underlying balance increases by only 990e18 due to the transfer fee.
3. `_buildDispatchPost` still encodes `amount: 1000e18` in the `Message` body and dispatches it.
4. On the destination chain, `onAccept` decodes `message.amount = 1000e18` and either mints 1000e18 on a `HyperFungibleToken` peer or unlocks 1000e18 of underlying from a `WrappedHyperFungibleToken` peer's escrow — 10e18 more than was actually locked, an unbacked mint/withdrawal.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L35-36)
```text
 * @notice Cross-chain wrapper for existing ERC20 tokens.
 * Locks the underlying token on the source chain and mints/unlocks on the destination chain.
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L234-253)
```text
    function _buildDispatchPost(HyperFungibleToken.SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(HyperFungibleToken.Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-273)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L322-324)
```text
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```

**File:** evm/src/apps/BridgeToken.sol (L26-29)
```text
 * @dev BRIDGE is native to nexus, so the two ends run the escrow model: `pallet-hyper-fungible-token`
 * escrows the native balance on nexus and this contract mints the equivalent here, meaning the supply
 * of this token is always backed by the pallet's escrow account. Sending back burns here and releases
 * there.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-301)
```text
        _mint(beneficiary, message.amount);
```

**File:** evm/src/apps/IntentGatewayV2.sol (L320-322)
```text
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
```
