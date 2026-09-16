### Title
Escrow release to a blocklisted `beneficiary` permanently locks IntentGatewayV2 escrow funds - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw()` performs an unconditional `IERC20(token).safeTransfer(beneficiary, amount)` to release escrowed order funds (solver payout on fill, or refund to the user on cancel/timeout). If `token` is a blocklist-capable stablecoin (e.g., USDC) and the `beneficiary` address is blocklisted, this transfer reverts, and there is no alternate pull-based recovery path, permanently freezing the escrowed funds for that order.

### Finding Description
`_withdraw` is the single settlement primitive used by both the same-chain fill path (`IntrinsicIntents._fillSameChain` / `_cancelSameChain`) and the cross-chain settlement path reached via `ExtrinsicIntents.onAccept` (processing `RedeemEscrow`/`RefundEscrow` messages delivered from Hyperbridge): [1](#0-0) 

For every token in the withdrawal request, the escrow accounting (`_orders[commitment][token] -= amount`) is decremented *before* the token transfer is attempted, and then `safeTransfer(beneficiary, amount)` is called directly with no try/catch or fallback. If the ERC20 is a blocklist-style token (USDC, USDT-style) and `beneficiary` is blocklisted, the transfer reverts, which reverts the entire `_withdraw` call — and thus the entire transaction that invoked it.

This is reachable from an unprivileged, single relayed message:
- On the source chain, a relayer delivers a cross-chain `RedeemEscrow` (solver claiming escrow after filling on the destination chain) or `RefundEscrow` (user cancellation) POST request via `onAccept`, which decodes a `WithdrawalRequest` and calls `_withdraw`.
- On the same chain, any solver calling `fillOrder`/`cancelOrder` triggers `_fillSameChain`/`_cancelSameChain`, which also call `_withdraw`.

Because the `beneficiary` in the `WithdrawalRequest` is fixed at order-placement/fill time (`order.user` for refunds, `msg.sender` solver for fills, both baked into `order`/commitment before settlement), there is no mechanism to designate an alternate address after the fact. Once USDC (or another blocklist-token) blocklists that specific `beneficiary`, every attempt to settle that order — including cancellation refund attempts by the user — reverts on the `safeTransfer` call, permanently freezing the escrowed principal in the gateway contract with no rescue path defined in the strategy/gateway code.

This mirrors the reported bug class in Gitcoin's `DonationVotingMerkleDistributionVaultStrategy.claim`, where a push-transfer directly to a claimant/recipient address reverts entirely if that address is blocklisted by USDC, and the pooled/escrowed funds become stuck with no accounting adjustment or pull-based recovery.

### Impact Explanation
If an attacker blocklists (or otherwise causes to be blocklisted) the `beneficiary` address that is due escrow release (the order's `user` on refund, or the filling `solver` on redemption), the specific order's escrowed input tokens become permanently locked in the `IntentGatewayV2`/`IntentsBase`-derived contract:
- Cross-chain solvers cannot claim their input-token payout via `RedeemEscrow` if their address gets blocklisted, even though they legitimately delivered the output tokens on the destination chain — this is a direct, permanent loss of the solver's funds.
- Users cannot recover their escrowed principal via `cancelOrder`/`RefundEscrow` if their own address becomes blocklisted after order placement.
- There is no way to update the beneficiary post-hoc or sweep/rescue escrow tied to a specific commitment once `_withdraw` starts reverting — this is a full, permanent freeze of that order's funds, satisfying "permanent freezing of funds."

This is High severity: it's a permanent, unrecoverable freeze of user/solver principal reachable by a single relayed message or fill/cancel call, with no privileged intervention required to trigger (the attacker just needs to get the counterparty's address blocklisted by the token issuer, which is documented USDC/USDT behavior — see https://github.com/d-xo/weird-erc20#tokens-with-blocklists).

### Likelihood Explanation
Likelihood is Medium-High for High-value stablecoin routes: USDC/USDT are extremely common `TokenInfo.token` choices for intent inputs/outputs on IntentGatewayV2 (tests in the repo explicitly use USDC as the input token — `evm/tests/foundry/IntentGatewayV2Test.sol`). While blocklisting requires cooperation/action from the centralized token issuer (Circle/Tether) or a legal/compliance action against a specific address, it is a well-known and documented weird-ERC20 behavior class, and any solver or user address can become blocklisted independent of the protocol's control. No governance or privileged action within Hyperbridge is required to trigger the freeze — only a state change on the token contract that the protocol does not defend against.

### Recommendation
Do not push-transfer the escrowed proceeds directly to `beneficiary` in `_withdraw`. Instead:
1. Decouple escrow release accounting from the token transfer: mark the order settled/finalized and credit an internal "claimable" balance for `beneficiary`, then let `beneficiary` (or anyone on their behalf) pull the funds via a separate `claim()` function.
2. Wrap the `safeTransfer` in a try/catch; on failure, keep the funds escrowed under a per-beneficiary claimable mapping (pull-based) rather than reverting the whole settlement, and allow the beneficiary to designate/rotate a payout address for the claim.
3. Alternatively, provide a governance/timelocked rescue path scoped per-commitment that allows redirecting stuck escrow to a new address after a grace period, so blocklisting one address cannot indefinitely freeze the underlying principal.

### Proof of Concept
1. User places a cross-chain order with USDC as an input token, escrowed into `IntentGatewayV2` on the source chain via `placeOrder`.
2. A solver fills the order on the destination chain via `fillOrder`, which dispatches a `RedeemEscrow` request to the source chain naming the solver's address as `beneficiary`.
3. Before the relayer delivers/executes the `RedeemEscrow` message on the source chain (or even after, if Circle blocklists later and a retry/cancel is attempted), the solver's address gets blocklisted by Circ 
 le (e.g., due to unrelated OFAC/compliance action, or an attacker reporting the address).
4. The relayer delivers the `RedeemEscrow` message; `onAccept` decodes it and calls `_withdraw`, which calls `IERC20(usdc).safeTransfer(solver, amount)` — USDC's `transfer` reverts because the recipient is blocklisted.
5. The entire `onAccept` transaction reverts. The escrow entry `_orders[commitment][usdc]` is never decremented (revert rolls back state), but every retry of delivering the same message hits the same revert — the solver can never claim, and there is no alternate withdrawal path, so the escrowed USDC is permanently stuck in the gateway contract. [1](#0-0) [2](#0-1)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L106-142)
```text
    /**
     * @notice The only relayer whose `onAccept` and `onGetResponse` deliveries are accepted, or
     * zero while the gate is open
     */
    function relayer() external view returns (address) {
        return _relayer;
    }

    /// @dev `kind` followed by the ABI-encoded `WithdrawalRequest`.
    function _body(RequestKind kind, bytes32 commitment, TokenInfo[] calldata tokens, bytes32 beneficiary)
        internal
        pure
        returns (bytes memory)
    {
        return bytes.concat(
            bytes1(uint8(kind)),
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: tokens, beneficiary: beneficiary}))
        );
    }

    /// @dev Posts `body` to the gateway on the order's source chain, paying `nativeFee` in native
    /// tokens when non-zero and in the fee token otherwise.
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```
