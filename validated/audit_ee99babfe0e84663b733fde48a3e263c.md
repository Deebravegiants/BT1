### Title
Reentrancy via post-transfer escrow accounting in `withdraw` allows draining shared escrow before `_orders` is decremented - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) still contains the exact CEI-violation pattern the sherlock report describes for `Boosted3TokenPoolUtils._redeem`: external token/native transfers to an attacker-influenced `beneficiary` are executed **before** the corresponding escrow accounting (`_orders[commitment][token]`) is decremented. The main EVM implementation (`evm/src/apps/intentsv2/IntentsBase.sol`) was already patched for this exact class of bug (see `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`), but the Tron contract was not brought up to the same standard.

### Finding Description
In `withdraw()`: [1](#0-0) 

the loop performs, per token:
1. Check `_orders[body.commitment][token] == 0`
2. External call: `beneficiary.call{value: amount}("")` (native) or `token.call(...transfer(beneficiary, amount)...)` (ERC20)
3. Only **after** the external call: `_orders[body.commitment][token] -= amount;`

The same unsafe ordering repeats for transaction fees a few lines below (external `feeToken.call(...transfer...)` happens, then `delete _orders[body.commitment][TRANSACTION_FEES];`).

Contrast with the already-fixed `IntentsBase._withdraw` in the main EVM app, where the escrow decrement happens *before* the transfer: [2](#0-1) 

`beneficiary` in `WithdrawalRequest` is attacker-controllable end-to-end: a solver fills a cross-chain order and sets `msg.sender` as the beneficiary embedded in the `RedeemEscrow` message dispatched back to the source chain: [3](#0-2) 

When that message is relayed, `onAccept` on the source (Tron) chain authenticates only the *message origin* (that it came from the registered sibling gateway instance), not the beneficiary, and calls `withdraw()` directly: [4](#0-3) 

No `ReentrancyGuard`/`nonReentrant` modifier is present anywhere in the Tron contract (confirmed by grep across the file). Since orders can escrow multiple input tokens (`_orders[commitment][token]` is per-(commitment, token), and the contract holds a single pooled balance per token across *all* orders), a malicious beneficiary contract — either receiving native TRX via its `receive()`, or acting as a malicious/attacker-supplied ERC20 input token with a transfer-hook style callback — regains control mid-loop, before that token's specific escrow slot is decremented. From there it can re-enter any externally reachable function of the same contract (e.g. `cancelOrder`, `placeOrder`, or another leg of a batched `handlePostRequests`/`handleGetResponses` call the relayer submitted in the same transaction) while `_orders[commitment][token]` (and, in the fee case, `_orders[commitment][TRANSACTION_FEES]`) still reflects the pre-withdrawal balance.

### Impact Explanation
This is a fund-safety issue reachable from a single relayed message plus an attacker acting as an ordinary, unprivileged solver/beneficiary. If the reentrant path can reach a second read of `_orders[commitment][token]` (or of the transaction-fee slot) before the first write completes, the same escrowed balance can be paid out more than once, or interleave with the fee payout, draining tokens that are pooled with — and thus effectively backed by — other users' escrowed orders in the same token. This matches the "concrete theft/permanent freezing of funds" bar: an attacker-controlled beneficiary contract can extract more value than it is legitimately owed from the gateway's shared token balance.

### Likelihood Explanation
Medium-High. The sponsor's own fix history shows this exact bug class was already identified and patched in the primary EVM implementation with an explicit regression test (`IntrinsicIntentsReentrancyTest.sol`), confirming it is both realistic and previously exploited/exploitable in this exact codebase — the Tron variant is simply an un-synced fork that reintroduces the identical unsafe ordering. The `beneficiary` and `token` values needed to arm the attack are both attacker-supplied (solver address and order input token, respectively), requiring no privileged role — only placing/filling an order.

### Recommendation
Apply the same Checks-Effects-Interactions fix already used in `IntentsBase._withdraw`: decrement `_orders[body.commitment][token]` (and delete the `TRANSACTION_FEES` entry) **before** performing the native/ERC20 transfer in `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw`. Additionally, consider adding a `nonReentrant` guard to `onAccept`/`withdraw` and `cancelOrder` as defense-in-depth, mirroring how the sponsor treated this issue as "fix just in case" in the original Sherlock discussion.

### Proof of Concept
Exact reentrant callback sequencing (which secondary function is reachable mid-loop, e.g. via a batched `handlePostRequests`/`handleGetResponses` call or a second escrow leg of the same multi-input order) was not independently fuzzed here; this is analogous to the exact pattern the maintainers already fixed in the sibling contract (`IntentsBase._withdraw`) with a dedicated regression test (`evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`), which documents the attack window as:
```
beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
// state (_orders / _filled) not yet updated
``` [5](#0-4) 
The Tron `withdraw()` function reproduces this same window for `_orders[...][token]` and `_orders[...][TRANSACTION_FEES]`, unpatched.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-48)
```text
/**
 * @title ReentrantBeneficiary
 * @notice Malicious beneficiary contract that attempts to re-enter `fillOrder` during
 *         the ETH transfer made by `_fillSameChain` or `_fillCrossChain`.
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
```
