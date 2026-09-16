### Title
Unauthenticated `CallDispatcher.dispatch()` lets anyone drain any residual ETH balance held by the shared dispatcher contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch(bytes)` is `external` with no access control (no `onlyHost`, no caller check whatsoever) and no `payable`/reentrancy guard. It decodes an attacker-supplied `Call[]` and, for each entry, does `to.call{value: call.value}(call.data)`, where `call.value` is paid out of the **dispatcher contract's own ETH balance** (not `msg.value`). The contract also implements `receive() external payable {}`, so it can passively accumulate ETH. Because `dispatch()` can be called directly by any unprivileged address — completely bypassing the ISMP `EvmHost`/`HyperFungibleToken`/`WrappedHyperFungibleToken` `onAccept` flow that is supposed to be the only caller — any ETH sitting in the dispatcher's balance at any point in time can be swept out by an attacker in a single transaction. [1](#0-0) 

### Finding Description
`CallDispatcher` is a shared, singleton-per-deployment utility contract referenced by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and their upgradeable variants via `ICallDispatcher(_dispatcher).dispatch(message.data)` inside `onAccept`. Its stated design intent (per documentation) is that it executes calls "in its own context (not via delegatecall)", and that cross-chain senders may set the transfer recipient (`to`) to the `CallDispatcher` address itself so that bridged tokens/ETH land there immediately before the attached `Call[]` payload spends them: [2](#0-1) 

The critical flaw is that `dispatch()` itself has zero caller restriction: [3](#0-2) 

Compare this to the `ICallDispatcher` interface's own description, which explicitly calls the payload "untrusted": [4](#0-3) 

The intended invocation path is:
1. `WrappedHyperFungibleToken.onAccept` (called only by the host) unwraps WETH and native-ETH-pushes `message.amount` to `beneficiary` (which can be set to the `CallDispatcher` address by the cross-chain sender).
2. It then calls `ICallDispatcher(_dispatcher).dispatch(message.data)` in the *same* transaction to spend that value.

But nothing prevents any external account from calling `CallDispatcher.dispatch()` **directly**, at any time, with an arbitrary `Call[]` whose `to`/`value`/`data` are fully attacker-controlled. Since `call.value` is paid from the dispatcher's own balance (not `msg.value` of the calling transaction), any ETH that is present on the dispatcher when the attacker's transaction executes — whether from (a) the `receive()` fallback accepting stray ETH sends, (b) a WHFT `onAccept` leaving residual native ETH if the attached `Call[]` in that message doesn't consume the full pushed amount (any non-zero remainder simply remains on the dispatcher after the transaction completes, since the call is fire-and-forget with no sweep-back), or (c) any other path that transiently routes ETH through this address — is immediately withdrawable by anyone who races a `dispatch()` call before it is consumed.

This directly mirrors the CVE-2022-4136 bug class: a "dangerous method exposed" that lets an unauthenticated caller invoke arbitrary downstream functionality (`to.call(data)` to any address, with any value) that was only meant to be reachable through a privileged/authenticated entry point (the ISMP host → app `onAccept` path).

### Impact Explanation
Any ETH balance that accumulates on a deployed `CallDispatcher` instance (shared across `HyperFungibleToken`/`WrappedHyperFungibleToken` deployments per the deploy scripts) is not protected by any access control and can be permanently stolen by any unprivileged third party via a directly-submitted transaction calling `dispatch()`. This is a concrete theft-of-funds vector: an attacker can drain leftover native-ETH balances (accidental transfers via `receive()`, or unspent remainders from WETH unwrap-and-forward flows in `WrappedHyperFungibleToken.onAccept`) at will, at zero cost beyond gas, ahead of the legitimate owner/recipient. It qualifies as High severity under the "concrete theft of funds" acceptance criterion because it requires only a single transaction from any address and no privileged role.

### Likelihood Explanation
Likelihood is High for any window in which the dispatcher holds a nonzero ETH balance: `dispatch()` has no gating whatsoever, so exploitation is a single, trivial, always-available transaction (`dispatch(abi.encode(Call[](to: attacker, value: dispatcher.balance, data: "")))`). The only precondition is a nonzero balance on the dispatcher, which is achievable either passively (its `receive()` accepts arbitrary ETH) or as a byproduct of the documented WETH-unwrap-to-dispatcher pattern in `WrappedHyperFungibleToken.onAccept` whenever a cross-chain message's attached `Call[]` does not consume 100% of the delivered native value.

### Recommendation
- Restrict `CallDispatcher.dispatch()` so it can only be invoked as part of the intended flow — e.g., require `msg.value`-scoped call values passed in by the caller rather than spending the dispatcher's stored balance, or make `dispatch` `payable` and forward only `msg.value`/explicitly-transferred funds rather than the contract's residual balance.
- Remove the unconditional `receive()` payable fallback, or add a sweep/refund mechanism so ETH cannot linger on the dispatcher between calls.
- In `WrappedHyperFungibleToken.onAccept`, ensure that if `beneficiary == _dispatcher`, the full pushed amount is guaranteed to be consumed by the attached calls (e.g., verify post-call balance is zero, or explicitly refund any remainder to a safe address) so no residual value can persist for a subsequent unauthenticated `dispatch()` call to steal.
- Consider adding a reentrancy/caller check so `dispatch()` can only be called by the token contracts that hold a legitimate reference to it (though care must be taken since it is intentionally meant to be a shared, permissionless utility — the safer fix is ensuring it never holds value between calls).

### Proof of Concept
1. Attacker sends 1 ETH directly to the deployed `CallDispatcher` address (accepted unconditionally by its `receive()` function), or alternatively waits for/triggers a `WrappedHyperFungibleToken.onAccept` delivery where `beneficiary == dispatcher` and the attached `Call[]` payload does not spend the full native amount pushed (e.g., a message with `data` whose calls only forward a fraction of `message.amount`).
2. Attacker calls `CallDispatcher.dispatch(abi.encode(Call[]({to: attackerAddr, value: address(dispatcher).balance, data: ""})))` directly, with no prior authorization from the host or any token contract.
3. `dispatch()` executes `to.call{value: call.value}(call.data)` unconditionally, transferring the dispatcher's full ETH balance to `attackerAddr`.
4. Confirmed by code inspection of `evm/src/utils/CallDispatcher.sol` lines 36-62: no `onlyHost`, no caller allowlist, no balance/ownership check exists anywhere in `dispatch()`.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L25-62)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-328)
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
```

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L26-36)
```text
/**
 * @title The ICallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This interface is used to dispatch untrusted call(s)
 */
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
```
