## Analog Found

### Title
Fee-on-transfer/deflationary underlying tokens let users unlock more on the destination chain than they actually locked, draining the wrapper's shared collateral pool - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` uses the caller-supplied `params.amount` both as the amount pulled via `safeTransferFrom` and as the amount encoded into the cross-chain `Message.amount` that the destination chain will mint/unlock against. It never checks how much the wrapper actually received. If the underlying token takes a fee/deflates on transfer, the wrapper locks less than `params.amount` while still claiming — and dispatching — the full `params.amount` as backing. This is the same root cause as the reported wfCash issue: a user-controlled "amount to credit" is decoupled from the actual value deposited, and the shortfall is silently absorbed by the shared pooled balance the contract already holds (other users' locked collateral), rather than being validated against what was truly received.

### Finding Description
In `send()`: [1](#0-0) 

```solidity
function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
    uint256 msgValue = msg.value;
    if (_isWeth && msgValue >= params.amount) {
        msgValue = msgValue - params.amount;
        IWETH(_underlying).deposit{value: params.amount}();
    } else {
        IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
    }

    DispatchPost memory request = _buildDispatchPost(params);
    ...
}
```

`_buildDispatchPost` encodes `amount: params.amount` verbatim into the `Message` body dispatched to the peer `HyperFungibleToken`/`WrappedHyperFungibleToken` on the destination chain: [2](#0-1) 

The destination side mints or unlocks exactly `message.amount`: [3](#0-2) 

Unlike `send()`, the `IntentGatewayV2.placeOrder()` code in this same codebase explicitly guards against this exact class of discrepancy by measuring the balance delta before/after `safeTransferFrom` and using the *actual received* amount for escrow accounting: [4](#0-3) 

`WrappedHyperFungibleToken.send()` (and its upgradeable twin) has no equivalent check — `params.amount` is trusted as-is for both the pull and the cross-chain credit, exactly mirroring the wfCash flaw where `depositAmountExternal` (actual value moved) and `fCashAmount` (claimed value credited) were independently controllable and the difference was covered by the wrapper's pre-existing pooled balance instead of reverting.

### Impact Explanation
Every `WrappedHyperFungibleToken` deployment holds a single shared pool of the underlying ERC20 backing all outstanding wrapped supply across every destination chain. If the underlying token ever applies a transfer fee, deflationary burn, or any other mechanism that makes `balanceOf` delta smaller than the transferred amount, any caller of `send()` can mint/unlock tokens on the destination chain that are not fully backed. Each such call permanently under-collateralizes the pool by the shortfall, and that shortfall is paid for out of other users' previously locked balances when they eventually try to redeem — a direct loss of funds / insolvency of the escrow, satisfying the "unbacked mint" and "theft/permanent freezing of funds" criteria.

### Likelihood Explanation
Reachable in a single unprivileged transaction (`send()`) by any token bridger; no relayer or consensus proof compromise is required — only that the configured `underlying` token exhibits fee-on-transfer or similarly deflating behavior, a common real-world ERC20 pattern the codebase itself already anticipates and defends against elsewhere (`IntentGatewayV2`).

### Recommendation
In `send()` (both `WrappedHyperFungibleToken.sol` and `WrappedHyperFungibleTokenUpgradeable.sol`, and any Tron/EVM equivalents), measure the actual amount received by diffing `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use that measured amount — not `params.amount` — both for the WETH branch bookkeeping and for the `Message.amount` encoded into the dispatched cross-chain body, so the destination-chain mint/unlock is always backed exactly by what was actually locked.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `underlying` set to a token that charges, e.g., a 1% fee on transfer (or a rebasing/deflationary token).
2. Attacker calls `send({dest, to: attacker, amount: 1000 tokens, ...})`.
3. `safeTransferFrom(attacker, wrapper, 1000)` actually delivers only 990 tokens to the wrapper (10 burned/fee'd away), but `_buildDispatchPost` still encodes `amount: 1000` in the dispatched `Message`.
4. On the destination chain, `HyperFungibleToken.onAccept` mints 1000 tokens to the attacker (or a peer `WrappedHyperFungibleToken` unlocks 1000 from its own pool).
5. The home-chain wrapper's underlying balance increased by only 990 while 1000 units of claim were created — a 10-unit deficit funded by the pool of prior depositors. Repeating this drains the pool over time, eventually causing legitimate `send()`/redemption calls to revert due to insufficient underlying balance (frozen funds) or race-condition losses for the last redeemers.

### Citations

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-290)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-313)
```text
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```
