### Title
Locked reserve accounting in `WrappedHyperFungibleToken.send()` does not account for fee-on-transfer/deflationary underlying tokens, causing unbacked minting and insolvency of the lock/unlock reserve - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)`, then dispatches a cross-chain `Message` whose `amount` field is the caller-specified `params.amount`, not the amount actually received into custody. If the configured underlying token charges a transfer fee (deflationary) or is a rebasing token whose balance can differ from the nominal transferred amount, the wrapper's actual custodied reserve is less than the amount it instructs the destination `HyperFungibleToken` to mint (or a peer `WrappedHyperFungibleToken` to unlock). This is the same accounting root cause flagged in the external report for `ZNSTreasury.stakeForDomain()` — recording a nominal amount instead of the actual reserve delta — but here it drives value creation/insolvency in a cross-chain bridge instead of a single-chain stake ledger.

### Finding Description
In `send()`:
```solidity
function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
    uint256 msgValue = msg.value;
    if (_isWeth && msgValue >= params.amount) {
        ...
    } else {
        IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
    }

    DispatchPost memory request = _buildDispatchPost(params);
    ...
}
``` [1](#0-0) 

`_buildDispatchPost` encodes `message.amount = params.amount` directly from the caller-supplied parameter: [2](#0-1) 

No balance-before/balance-after measurement is performed around the `safeTransferFrom` call, unlike the pattern already implemented elsewhere in the codebase for this exact class of token (fee-on-transfer). `IntentGatewayV2.placeOrder()` explicitly measures `balBefore`/`balAfter` and mutates `order.inputs[i].amount` to the actually-received amount before computing the escrow and commitment:
```solidity
uint256 balBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
``` [3](#0-2) 

`WrappedHyperFungibleToken.send()` has no equivalent correction. If the underlying token is deflationary/fee-on-transfer, the wrapper receives `params.amount - fee` but still tells the destination chain to mint/unlock the full `params.amount`. On the remote `HyperFungibleToken`, `onAccept` unconditionally mints the message amount to the beneficiary:
```solidity
Message memory message = abi.decode(request.body, (Message));
address beneficiary = _toAddr(message.to);
_mint(beneficiary, message.amount);
``` [4](#0-3) 

This creates newly minted supply on the remote chain that is not fully backed by the locked reserve on the home chain. The same discrepancy applies on the reverse leg: `onAccept` in `WrappedHyperFungibleToken` unlocks the full `message.amount` via `safeTransfer`, again without verifying the wrapper's actual holdings cover it: [5](#0-4) 

### Impact Explanation
Each `send()` call with a deflationary underlying leaks a small amount of "phantom" backing. Over repeated sends this compounds into a systemic shortfall between the home-chain locked reserve and the aggregate remote-chain minted supply. Eventually, legitimate users trying to bridge back (unlock) will find the wrapper's reserve insufficient, reverting their unlock and permanently freezing their funds, while other users may have already extracted more value than they locked — an unbacked mint / cross-chain insolvency scenario. This satisfies the "concrete theft or permanent freezing of funds, unbacked mint" bar.

### Likelihood Explanation
Reachable by any unprivileged token bridger via a single `send()` transaction; no special permissions are required beyond normal token approval. It is fully triggered by the owner's choice of `underlying` token during `configure()` (comparable to the zNS parent domain owner choosing a payment token in the original report) — a token property decision, not an admin exploit, so this is not excluded by the malicious-admin exclusion rule. Any deflationary/fee-on-transfer ERC20 configured as `underlying` triggers the bug on every `send()` call.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2.placeOrder()`: measure the wrapper's underlying token balance immediately before and after `safeTransferFrom`, and use the actual delta (not `params.amount`) as `message.amount` in `_buildDispatchPost`. Apply the same correction to `WrappedHyperFungibleTokenUpgradeable.send()` and to any unlock path that trusts a nominal amount without verifying available reserve.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` and `configure()` it with an ERC20 `underlying` that charges, e.g., a 1% fee on transfer (as in the `FeeOnTransferToken` test helper already present in the test suite at `evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2690-2730`).
2. User calls `send(params)` with `params.amount = 1000e18`. `safeTransferFrom` moves only 990e18 into the wrapper (10e18 fee retained by the token/burned).
3. `_buildDispatchPost` still encodes `message.amount = 1000e18`.
4. On the destination chain, `HyperFungibleToken.onAccept` mints the beneficiary 1000e18 — 10e18 more than was ever actually locked.
5. Repeating this drains the wrapper's true backing ratio; a later unlock request for the full nominal amount will revert (`safeTransfer` fails once reserve is depleted), freezing funds for the affected user while earlier users have already received unbacked minted supply.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L319-323)
```text
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L299-301)
```text
        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);
```
