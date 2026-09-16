## Analog Found

### Title
Escrow redemption/refund permanently reverts and locks funds if the beneficiary cannot receive ETH or is blocklisted by the ERC-20 token - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
The Hyperbridge Intent Gateway's `_withdraw` function pays out escrowed order inputs to a `beneficiary` address that is embedded in a cross-chain `WithdrawalRequest` and is not chosen by whoever delivers the settlement message. If that fixed beneficiary is a smart contract that rejects native ETH transfers, or an address blocklisted by the escrowed ERC-20 (e.g. USDC), the payout call reverts unconditionally and the escrowed funds can never be released — exactly the address-restriction/permanent-freeze pattern described in the FootiumPrizeDistributor report.

### Finding Description
`_withdraw` in `IntentsBase.sol` derives the recipient directly from the message body and transfers funds to it with no fallback: [1](#0-0) 

- For native-asset inputs it calls `_sendValue(beneficiary, amount)`, which reverts with `InsufficientNativeToken` if the low-level call fails: [2](#0-1) 
- For ERC-20 inputs it calls `IERC20(token).safeTransfer(beneficiary, amount)`, which reverts if the token enforces a blocklist (e.g., USDC-style compliance) against the beneficiary.

`beneficiary` is not supplied by the caller delivering the message and cannot be redirected — it comes straight from the on-chain `WithdrawalRequest.beneficiary`, which for `RedeemEscrow` is fixed to `msg.sender` of the filler at fill time (`bytes32(uint256(uint160(msg.sender)))`), and for `RefundEscrow`/same-chain cancel is fixed to `order.user`: [3](#0-2) [4](#0-3) 

Because the beneficiary is baked into the committed order/message and cannot be changed after the fact, once it is an address that structurally cannot receive the payout (non-payable contract for native assets, or blocklisted for the ERC-20), the `_withdraw` call always reverts. There is no separate "claim to a different address" step as recommended in the source report, unlike `WrappedHyperFungibleToken`, which explicitly guards this exact scenario by falling back to a WETH transfer if the native push fails: [5](#0-4) 

`IntentsBase._withdraw` (used by both the cross-chain `RedeemEscrow`/`RefundEscrow` `onAccept` handler and the same-chain fill/cancel paths) has no equivalent fallback for native transfers, and none at all for ERC-20 blocklisting.

### Impact Explanation
When triggered, the escrowed input tokens (deposited by the order's user at `placeOrder`) become permanently stuck in the `IntentGatewayV2` contract:
- On the fill path, a solver's chosen `msg.sender` fill address being a non-payable contract or a blocklisted address for the input token permanently prevents the solver from ever claiming the tokens it is owed for delivering output assets, since the settlement message can never be successfully processed. This is not merely an inconvenience to the individual solver — the associated escrow (potentially involving large sums for popular tokens) is permanently frozen in the contract with no recovery path.
- On the cancel/refund path, if the order's `user` address (fixed at order placement) is later blocklisted by the token issuer, or is a contract that cannot receive native assets, the user's own funds are locked forever with no other party able to redirect the refund.

This matches the "permanent freezing of funds" severity bar since there is no on-chain mechanism to change the beneficiary or retry with an alternate address once the message/commitment has been finalized.

### Likelihood Explanation
Likelihood is moderate: reaching this state requires either (a) a solver/filler operating from a smart-contract wallet without a `receive()`/payable fallback when settling native-asset orders, or (b) an escrowed ERC-20 (such as USDC) blocklisting the beneficiary address after order placement but before settlement — a realistic scenario for any project bridging USDC-class tokens with issuer-controlled blocklists. Both are plausible in production usage of the Intent Gateway given native-ETH orders and stablecoin-based routes are core supported flows.

### Recommendation
Do not hard-fail the entire withdrawal on a failed transfer to the fixed beneficiary. For native-asset legs, mirror the `WrappedHyperFungibleToken` pattern: on a failed low-level ETH push, wrap into WETH (or another pull-based escrow) and transfer that as ERC-20 instead of reverting. For ERC-20 legs (or as a general hardening), if `safeTransfer` to the beneficiary reverts, credit the amount to an internal, beneficiary-keyed "pending withdrawal" balance that anyone (including the beneficiary from an alternate address, via a signed authorization) can later pull-claim, rather than reverting the whole settlement and leaving funds stuck with no path forward.

### Proof of Concept
1. A solver fills a cross-chain order using a smart-contract `msg.sender` (e.g., a vault/proxy contract with no `receive()`/payable fallback) for a native-ETH-denominated order, or one that is later added to a token's blocklist for an ERC-20-denominated order.
2. The order is filled successfully on the destination chain (`fillOrder`), dispatching a `RedeemEscrow` message with `beneficiary = filler` back to the source chain: `evm/src/apps/intentsv2/ExtrinsicIntents.sol` lines 206-220.
3. When the relayer delivers this message to the source chain's `onAccept`, `_withdraw` is invoked with the fixed `beneficiary`: `evm/src/apps/intentsv2/IntentsBase.sol` lines 451-470.
4. The native transfer via `_sendValue` (line 419-422) or ERC-20 `safeTransfer` reverts because the beneficiary contract has no payable fallback / is blocklisted.
5. Since `beneficiary` cannot be altered post-commitment (it is fixed in the settled order/message), every retry of delivering this message reverts identically, permanently locking the escrowed input tokens in `IntentGatewayV2` with no recovery mechanism.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
    }
```

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L206-220)
```text
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
    }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L126-130)
```text
        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);

```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-324)
```text
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
