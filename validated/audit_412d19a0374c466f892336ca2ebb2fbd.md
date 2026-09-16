### Title
Fee-on-transfer / rebasing underlying tokens break the 1:1 lock-and-credit invariant in `WrappedHyperFungibleToken`, permanently freezing bridged funds - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` pulls `params.amount` of the underlying ERC20 via `safeTransferFrom` and then dispatches a cross-chain message that unconditionally credits the destination chain with the full `params.amount`, without ever verifying that the contract's actual token balance increased by that amount. This is the same root-cause class as the external report: an asset whose transfer semantics don't preserve a strict 1:1 balance change (fee-on-transfer, deflationary, or rebasing tokens) causes the wrapper's internal accounting (messages crediting fixed amounts) to drift from its real custodied balance, and there is no reconciliation or recovery mechanism to fix the resulting shortfall/excess.

### Finding Description
`send()` does:
```solidity
IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
...
DispatchPost memory request = _buildDispatchPost(params); // body.amount = params.amount
``` [1](#0-0) 

The dispatched `Message.amount` is always `params.amount` — the *requested* amount, not the amount actually received by the contract: [2](#0-1) 

On the remote chain, `HyperFungibleToken`/`HyperFungibleTokenUpgradeable` mints exactly `message.amount` new tokens to the beneficiary, fully trusting the amount encoded in the message body. When those minted tokens are later bridged back, `onAccept` on this wrapper unlocks the underlying by doing a plain `safeTransfer(beneficiary, message.amount)` against whatever balance the contract happens to hold: [3](#0-2) 

If the owner (via `configure`) ever points `_underlying` at a token that is fee-on-transfer, deflationary-on-transfer, or otherwise does not deliver the full nominal amount to `address(this)` on `safeTransferFrom` (or whose balance can decrease independently of transfers, e.g. rebasing-down), the contract will:
- credit the destination chain with more supply than it actually custodies (under-collateralization), or
- accumulate an un-tracked surplus that no function can retrieve, mirroring the wstETH "excess" scenario.

There is no `sweep`/`recoverExcess` function anywhere in the contract, and no invariant check comparing `balanceOf(address(this))` before/after `safeTransferFrom` against `params.amount`. This is structurally identical to the reported class of bug: assets with non-standard transfer semantics silently desynchronize the wrapper's internal ledger (the cross-chain messages) from its actual custody balance, and the protocol provides no recovery path once that happens.

### Impact Explanation
Once under-collateralization occurs, later legitimate bridge-back requests to this wrapper via `onAccept` will revert or drain the contract's remaining balance unfairly (first-come-first-served insolvency), permanently freezing funds for users whose mint on the remote chain is otherwise valid but whose corresponding underlying was never fully locked here. This is a protocol-level freezing-of-funds condition reachable by any unprivileged caller who invokes `send()` against a misbehaving/incompatible underlying token registered by the token's owner, and it directly parallels "no recovery for excess/deficit tokens" reported for wstETH. This qualifies as Medium/High since it results in permanent loss of user funds and breaks the accounting invariant the cross-chain bridge depends on for solvency.

### Likelihood Explanation
Likelihood depends on the owner configuring `_underlying` to a non-standard ERC20 (fee-on-transfer or rebasing) via `configure()`. Since `configure()` is owner-gated but the underlying token itself is not validated for standard-compliant transfer semantics anywhere in the contract, any deployment targeting such a token (a realistic and common occurrence in multi-chain token-gateway deployments where the operator doesn't fully vet every asset) immediately exposes this issue to every ordinary user calling `send()` — no privileged or malicious actor is required to trigger the drift itself, only to have configured the asset.

### Recommendation
Measure the actual amount received by reading `balanceOf(address(this))` before and after `safeTransferFrom` in `send()`, and use that delta (not `params.amount`) as the amount encoded in the dispatched message and credited on the destination chain. Reject configuration of underlying tokens whose transfer semantics do not preserve exact balances (or explicitly document/support only standard ERC20s), and add an owner-only sweep function to recover any balance in the wrapper that exceeds the sum of outstanding locked commitments, so any excess is not permanently unrecoverable, mirroring the fix recommended for wstETH.

### Proof of Concept
1. Owner deploys `WrappedHyperFungibleToken` and calls `configure()` with `underlying` set to a fee-on-transfer ERC20 (e.g., 2% transfer fee).
2. Alice calls `send({ amount: 100, ... })`; `safeTransferFrom` moves only 98 tokens into the wrapper (2 burned as fee), but `_buildDispatchPost` still encodes `amount: 100` in the ISMP message. [1](#0-0) 
3. On the destination chain, `HyperFungibleToken` mints Alice 100 tokens, fully trusting `message.amount`.
4. Alice (or anyone holding the minted 100 tokens) bridges back 100 tokens; `onAccept` attempts `safeTransfer(beneficiary, 100)` from the wrapper, but the wrapper only ever held 98 — for subsequent users this shortfall compounds and eventually the wrapper cannot honor unlocks, permanently freezing funds for the users whose bridge-back request lands once the balance is exhausted. [3](#0-2)

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-336)
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
