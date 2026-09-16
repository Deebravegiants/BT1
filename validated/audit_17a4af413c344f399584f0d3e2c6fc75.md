### Title
Missing reentrancy guard on Tron `IntentGatewayV2.placeOrder` allows escrow-commitment desync via ERC20/TRC20 sender-hook reentrancy - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` (`evm/tron/contracts/apps/IntentGatewayV2.sol:338`) lacks the `nonReentrant` modifier that the canonical EVM implementation applies to the same function (`evm/src/apps/IntentGatewayV2.sol:194`, which is `public payable nonReentrant` and inherits `ReentrancyGuardTransient`). The Tron contract inherits only `HyperApp, EIP712` — no reentrancy guard at all — while it still calls `IERC20(token).safeTransferFrom(msg.sender, ...)` on attacker-controlled token addresses before crediting escrow.

### Finding Description
In `placeOrder`, the nonce/commitment/escrow bookkeeping (`order.nonce = _nonce++;`, commitment computation, and `_orders[commitment][token] += reducedInputs[i].amount;`) happens interleaved with external `IERC20.safeTransferFrom` calls to attacker-supplied token contracts (`evm/tron/contracts/apps/IntentGatewayV2.sol:344-468`). On Tron, TRC20 tokens are not guaranteed to be simple, hookless transfers — many TRC20/TRC-like tokens (and any malicious token an attacker deploys and includes as an "input" token) can execute arbitrary code during `transferFrom`/`transfer` (e.g. via a callback to the sender or a hook triggered during the transfer). Because the EVM sibling contract explicitly needed a `nonReentrant` guard on this exact function to prevent balance/escrow desync from reentrant `placeOrder` calls (evidenced by the guard added there and by the dedicated `IntrinsicIntentsReentrancyTest.sol` suite covering CEI fixes for `fillOrder`), the absence of any reentrancy protection in the Tron port reintroduces the same class of bug: a malicious token used as an `order.inputs[]` asset can re-enter `placeOrder` (or other state-mutating entry points) mid-transfer. Because `_nonce++` and the commitment hash are computed per call, and escrow uses `+=`, a reentrant second `placeOrder` call using the same or a related order can complete its own transfer/escrow accounting and increment `_nonce` before the outer call's `safeTransferFrom` returns and its own escrow credit executes, allowing the order accounting to diverge from actual tokens received by the gateway — mirroring exactly the described L1BatchBridgeGateway bug class (reentering a deposit-style function via a token with sender hooks before the guard/state update takes effect).

### Impact Explanation
This can result in the intent gateway's escrow accounting (`_orders[commitment][token]`) reflecting more tokens than were actually transferred into the contract, or duplicate/overlapping order state due to `_nonce` desynchronization across reentrant calls. Since escrow amounts back solver fills and cross-chain settlement, an inflated or desynced escrow entry can be drained by a colluding/self-filling solver (theft of other users' or protocol funds) or can leave legitimate orders permanently unfillable/unrefundable (frozen funds) once the mismatch surfaces during fill/redeem. This satisfies "concrete theft or permanent freezing of funds" for the token-bridging/intents escrow path, matching the scope's included categories (intents escrow and bids, token bridge functions).

### Likelihood Explanation
Reachable by any unprivileged user submitting a single `placeOrder` transaction using a token they control as one of `order.inputs[]` — no admin, governance, or privileged role is required, matching the "single submitted transaction ... token transfer or order" reachability bar. The attack requires only deploying/using a token with a transfer hook (fully within an ordinary user's capability on Tron/EVM-compatible chains), the same precondition the external report used for `depositERC20`.

### Recommendation
Add a reentrancy guard (e.g. OpenZeppelin `ReentrancyGuard`/`ReentrancyGuardTransient`, consistent with `evm/src/apps/IntentGatewayV2.sol`) to `placeOrder` (and any other token-pulling entry points) in `evm/tron/contracts/apps/IntentGatewayV2.sol`, or restructure the function to follow strict checks-effects-interactions: finalize `_nonce`, commitment, and `_orders[...]` state only after all external token transfers have completed and their actual received amounts are measured (as the EVM version already does via balance-delta accounting), never interleaving state writes between multiple external calls without a guard.

### Proof of Concept
1. Attacker deploys a malicious TRC20 token `EvilToken` whose `transferFrom` callback re-enters `IntentGatewayV2.placeOrder` on the Tron gateway.
2. Attacker calls `placeOrder(order1, graffiti)` with `order1.inputs[0].token = EvilToken`, `amount = X`.
3. Inside `IERC20(EvilToken).safeTransferFrom(msg.sender, address(this), X)` (`evm/tron/contracts/apps/IntentGatewayV2.sol:459`), `EvilToken` calls back into `placeOrder(order2, ...)` before returning.
4. Because there is no `nonReentrant` modifier (unlike `evm/src/apps/IntentGatewayV2.sol:194`), the reentrant call executes fully: it increments `_nonce`, computes its own commitment, and credits `_orders[commitment2][EvilToken] += ...` based on a transfer that has not yet actually settled its full accounting relative to the outer call.
5. Control returns to the outer call, which also credits `_orders[commitment1][EvilToken] += reducedInputs[i].amount` using the same nominal `X`, even though the token's actual balance movements may not correspond 1:1 (e.g., fee-on-transfer/rebasing/hook logic can make the two calls jointly credit more escrow than tokens actually held by the gateway).
6. The gateway now believes it holds `escrow1 + escrow2` worth of `EvilToken`, while its actual `EvilToken` balance can be manipulated by the token's hook logic to be less — enabling a solver fill/redeem to drain more than was deposited, or causing a later fill to revert and permanently lock the legitimately-placed order's funds. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-386)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
        }

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L60-60)
```text
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-196)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

```
