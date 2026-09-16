## Title
`WrappedHyperFungibleToken.send()` mints cross-chain credit for the pre-fee amount instead of the amount actually locked, causing custody shortfall and insolvency with fee-on-transfer underlying tokens - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` assumes that calling `safeTransferFrom(msg.sender, address(this), params.amount)` always increases the contract's underlying token balance by exactly `params.amount`. It then encodes `params.amount` (the requested amount) into the cross-chain `Message` dispatched to the remote `HyperFungibleToken`, rather than the amount actually received. This mirrors the LIDO bug class: an accounting value used to back cross-chain claims is derived from the *requested* transfer amount instead of the *actually settled* amount, and the two can diverge.

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

`_buildDispatchPost` encodes the `Message.amount` field directly from `params.amount`: [2](#0-1) 

There is no check of the wrapper's actual token balance delta after `safeTransferFrom`. If `_underlying` is a fee-on-transfer (or rebasing/deflationary) ERC20, the wrapper's custody balance increases by less than `params.amount`, but the message that reaches the remote chain still carries the full `params.amount`.

On the remote chain, `HyperFungibleToken.onAccept()` mints exactly `message.amount` to the beneficiary: [3](#0-2) 

When that minted balance is later bridged back, `HyperFungibleToken` burns it and dispatches a message carrying the same full amount, which `WrappedHyperFungibleToken.onAccept()` unconditionally pays out of its custody balance via `safeTransfer`: [4](#0-3) 

Every fee-on-transfer `send()` call therefore creates a permanent shortfall between the home-chain custody balance (the true backing) and the total remote-chain minted supply (the claimed backing) — exactly analogous to `lidoLockedETH` being incremented by the *requested* withdrawal amount but only decremented by the *actually claimed* amount after a LIDO slashing event.

This is architecturally the same bug class as the reported IntentGatewayV2 fee-on-transfer fix, which was already addressed there by computing escrow from the *received* balance delta: [5](#0-4) 
`WrappedHyperFungibleToken` (and its upgradeable variant) never received the equivalent fix.

### Impact Explanation
As fee-on-transfer sends accumulate, `WrappedHyperFungibleToken`'s underlying balance becomes insufficient to back all tokens minted on remote chains. This is a race-to-exit / bank-run scenario just like the LIDO report: whichever user unwinds first can still be paid in full, but the last users attempting to unlock/withdraw will find the contract's underlying balance depleted, causing `safeTransfer` to revert and their funds to be permanently frozen (unable to redeem minted remote-chain balances back into the canonical asset). This constitutes both permanent freezing of funds and an unbacked-mint condition on the remote chain (`HyperFungibleToken` supply exceeds what `WrappedHyperFungibleToken` custody can honor).

### Likelihood Explanation
Any unprivileged user can trigger this simply by calling `send()` with a fee-on-transfer or deflationary ERC20 configured as `_underlying`. The vulnerability requires only that such a token be configured/whitelisted as the wrapped underlying — a plausible deployment configuration since `configure()` accepts any ERC20 address without restricting to non-fee tokens. Likelihood is low-to-medium since it depends on the underlying token type chosen at deployment, but once such a token is used, the shortfall accrues deterministically on every send, making eventual insolvency certain rather than probabilistic.

### Recommendation
In `send()`, measure the wrapper's actual balance before and after `safeTransferFrom` (or use the delta) and use that received amount — not `params.amount` — both for the dispatched `Message.amount` and for the fee/refund accounting, mirroring the fix already applied in `IntentGatewayV2` for fee-on-transfer tokens. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.sol`.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` and `configure()` it with a fee-on-transfer ERC20 (e.g., 1% transfer fee) as `_underlying`.
2. Call `send({ amount: 1000e18, ... })`: `safeTransferFrom` moves 1000e18 from the caller, but the wrapper's actual balance only increases by 990e18 (1% fee burned/redirected).
3. The dispatched `Message.amount` is still `1000e18`.
4. On the remote chain, `HyperFungibleToken.onAccept()` mints `1000e18` to the beneficiary — 10e18 more than what is actually custodied on the home chain.
5. Repeat across multiple sends; the home-chain wrapper's balance falls further and further behind total remote-chain minted supply.
6. Eventually, a legitimate `onAccept()` unlock request on the home chain reverts because `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` exceeds the wrapper's actual token balance, permanently freezing that user's funds — reproducing the same "last user cannot redeem" insolvency scenario described in the LIDO report.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-324)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2544-2556)
```text
        // Reconstruct commitment: inputs mutated to received, then reduced by protocol fee
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = expectedEscrow; // commitment is hashed with reduced amount
        bytes32 commitment = keccak256(abi.encode(order));

        assertEq(
            gatewayWithFees._orders(commitment, address(fot)),
            expectedEscrow,
            "Escrow should equal received minus protocol fee"
        );
    }
```
