### Title
Permanent loss of funds: zero-address beneficiary is not rejected before native ETH is pushed in `WrappedHyperFungibleToken.onAccept` - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.onAccept` decodes the cross-chain `Message.to` field and derives `beneficiary` via `_toAddr`, which only validates that the byte slice is 20 bytes long — it never rejects `address(0)`. When the wrapper is configured for a WETH-backed native asset (`_isWeth == true`), the contract unconditionally unwraps WETH and pushes native ETH to `beneficiary` with a raw low-level `call`. A `call{value: x}("")` to `address(0)` succeeds (it behaves like sending ETH to any EOA), so the ETH is transferred and permanently unrecoverable, unlike the ERC20 branch which is protected by OpenZeppelin's built-in zero-address check in `safeTransfer`.

### Finding Description
`_toAddr` only checks the length of the encoded address, not that it is non-zero: [1](#0-0) 

`onAccept` decodes the message and uses this unchecked beneficiary directly in the native-ETH delivery path: [2](#0-1) 

In the `_isWeth` branch, `IWETH(_underlying).withdraw(message.amount)` converts the escrowed WETH into native ETH held by the contract, and then `beneficiary.call{value: message.amount}("")` pushes it out. If `beneficiary == address(0)`, this low-level call succeeds (no code check is performed for value-only sends to an address with no code), so the funds leave the contract and are burned forever at `address(0)`. The fallback re-wrap path (`if (!sent) { ... }`) is never triggered because the call to `address(0)` reports success.

`message.to` originates from the source chain's `send()` call, where `params.to` is arbitrary caller-supplied bytes with no validation: [3](#0-2) 

By contrast, the ERC20 (`!_isWeth`) branch and the analogous `HyperFungibleToken.onAccept`/`onPostRequestTimeout` mint paths are safe, because OpenZeppelin's `ERC20._mint`/`ERC20.transfer` (via `SafeERC20.safeTransfer`) revert on a zero recipient. This makes the native-ETH branch of `WrappedHyperFungibleToken` the only unprotected path, directly analogous to the reported DODO GSP issue where `_mint`/`buyShares` lacked a zero-address check while the rest of the accounting assumed a valid recipient.

### Impact Explanation
Any cross-chain transfer for a WETH-backed `WrappedHyperFungibleToken` deployment whose destination address encodes to `address(0)` (e.g., due to a client bug, a malformed/forged `to` field, or a griefing relayer/dispatcher error during the calldata/message construction) results in the escrowed ETH being unwrapped and irrecoverably burned at `address(0)` instead of being safely retained or reverted. This is a permanent, unrecoverable loss of user funds for the affected transfer amount, satisfying the "permanent freezing/loss of funds" impact bar.

### Likelihood Explanation
The path is reachable directly from `onAccept`, which is invoked by the `IsmpHost` for every valid, correctly-proven incoming POST request — no privileged or malicious-admin actions are required. The only condition is that the decoded `message.to` resolves to the zero address, which can happen from a simple client-side integration bug (e.g. a caller passing `bytes(0)` or a badly padded encoding) with no on-chain validation catching it either at dispatch (`send`) or at delivery (`onAccept`). Given this contract is explicitly designed to also handle native ETH refunds/transfers (unlike the OZ-guarded ERC20/mint paths elsewhere in the codebase), the likelihood of at least one such misencoded transfer occurring in production is non-trivial.

### Recommendation
Add an explicit zero-address check in `_toAddr` (or immediately after deriving `beneficiary`/`refundee` in `onAccept` and `onPostRequestTimeout`) and revert if the decoded address is `address(0)`, mirroring the protection already provided incidentally by OpenZeppelin's ERC20 for the non-WETH branch. This ensures the native ETH branch fails closed instead of silently burning funds.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` configured with `_isWeth = true` and register a peer chain.
2. From the peer chain, send a POST request whose body decodes to `HyperFungibleToken.Message{ to: <19 or 20 zero bytes>, amount: X, ... }` (an attacker/integrator-controlled `params.to` on the source-chain `send()` call, or any malformed encoding that resolves to 20 zero bytes).
3. The relayer delivers this request; `IsmpHost` calls `onAccept`.
4. `_toAddr` returns `address(0)` (passes the length check).
5. `IWETH(_underlying).withdraw(X)` converts WETH to ETH held by the contract; `address(0).call{value: X}("")` succeeds.
6. `X` ETH is now permanently lost at `address(0)`; `sent == true` so the ERC20 fallback re-wrap never executes, and no revert occurs.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L370-376)
```text
    /// @notice Extracts an address from the first 20 bytes of a bytes memory value
    function _toAddr(bytes memory b) internal pure returns (address addr) {
        if (b.length != 20) revert InvalidAddress(b.length);
        // casting to 'bytes20' is safe because we already checked length
        // forge-lint: disable-next-line(unsafe-typecast)
        return address(bytes20(b));
    }
```
