### Title
`WrappedHyperFungibleToken` locks/unlocks a fixed nominal amount instead of the underlying's actual escrowed balance, breaking accounting for rebasing/fee-on-transfer ERC20s - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` and `onAccept()` (and their timeout-refund counterpart) assume a static 1:1 relationship between the nominal `amount` field carried in the cross-chain message and the actual quantity of underlying ERC20 tokens held in the contract's custody. For tokens whose balances can change outside of transfers (rebasing tokens) or that deduct a fee on transfer, this assumption is false, exactly the bug class described in the Nibiru finding.

### Finding Description
`send()` locks tokens with a plain `safeTransferFrom` and encodes the caller-specified `params.amount` into the outgoing message without ever checking the contract's actual balance delta: [1](#0-0) 

`onAccept()` then unconditionally transfers out the *nominal* `message.amount` from custody, again with no reference to the contract's real ERC20 balance: [2](#0-1) 

The same static-amount pattern appears in the timeout refund path: [3](#0-2) 

This is precisely the invariant that failed in the Nibiru report: "if an asset is created as an ERC20 and some amount is converted... a balance of the ERC20 is left inside the module account in order to convert back" — an assumption that silently breaks for rebasing or fee-on-transfer tokens, because the escrowed balance can drift up or down relative to the sum of nominal amounts recorded in outstanding cross-chain messages. Note that the sibling `IntentGatewayV2` contracts in the same repo explicitly guard against this class of bug by measuring `balanceOf` before/after transfers (see `evm/src/apps/IntentGatewayV2.sol:301-322` and the dedicated `FeeOnTransferToken` test suite), which shows the pattern is understood and mitigated elsewhere in this codebase but is missing from `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`.

### Impact Explanation
- **Negative rebase / fee-on-transfer deflation**: the escrow balance can fall below the sum of nominal amounts owed to pending cross-chain messages. When `onAccept` (or the timeout refund) tries to `safeTransfer` the full nominal `message.amount`, it will revert with insufficient balance, permanently freezing legitimate recipients' funds (a `PostRequestTimeout`/relayed message becomes undeliverable, and refunds on timeout can equally fail).
- **Positive rebase**: surplus tokens accumulate in the contract with no path to distribute or recover them, i.e., unbacked/unclaimable value stuck in the bridge contract.
- Because the contract is a token-bridge lock/unlock (mint-analog) primitive reachable by any user calling `send()` with an arbitrary configured underlying ERC20, this is a concrete freezing-of-funds / broken-accounting bug in the token bridge escrow logic, matching the Medium-severity classification given to the analogous Nibiru finding.

### Likelihood Explanation
Any owner-configured underlying token that is rebasing or fee-on-transfer will trigger this immediately and deterministically on the very next `onAccept`/timeout after a rebase event or transfer-fee deduction, with no special conditions or attacker requirement — a single ordinary user transaction (`send`) followed by an ordinary relayed delivery is enough to expose the mismatch.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2`: measure `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom` in `send()` and encode the *actual received* amount in the dispatched message rather than the caller-supplied `params.amount`; likewise, in `onAccept`/timeout-refund, either cap the transferred amount to the current available balance or reject/queue the transfer if the recorded amount cannot be honored, and document that only standard (non-rebasing, non-fee-on-transfer) ERC20s are supported for `_underlying`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with a rebasing ERC20 as `_underlying` (e.g., a token that reduces holder balances by X% per rebase, or a fee-on-transfer token).
2. Alice calls `send({ amount: 1000, ... })`; `safeTransferFrom` pulls 1000 nominal units, but due to a transfer fee the contract only actually receives 990. The dispatched message nonetheless encodes `amount: 1000`.
3. A negative rebase occurs on the underlying token while the message is in flight, further reducing the contract's actual balance below 990.
4. When the message is delivered on the destination chain's paired `WrappedHyperFungibleToken` deployment (or, in the lock/unlock same-chain replay case, when `onAccept` executes), `IERC20(_underlying).safeTransfer(beneficiary, 1000)` reverts because the contract's balance is insufficient, permanently blocking delivery of the recipient's funds; or, if `send()`/timeout math had instead locked more per-message accounting than truly held, other legitimate users' withdrawals of already-escrowed principal likewise fail.

### Citations

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-365)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```
