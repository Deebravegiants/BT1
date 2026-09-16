### Title
Predispatch escrow accounting reads the shared `CallDispatcher`'s raw token balance instead of a before/after delta, letting anyone donate tokens directly to it and have them misappropriated into an unrelated order or protocol "dust" - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder`'s predispatch path measures how much a predispatch swap produced by reading the *absolute* balance of the shared `CallDispatcher` contract (`IERC20(token).balanceOf(dispatcher)`), rather than a before/after delta scoped to the predispatch call it just executed. `CallDispatcher` is a single, permissionless, publicly-addressable contract shared by every order and every user of the gateway (and by `HyperFungibleToken`/`WrappedHyperFungibleToken` as well), with an unrestricted `receive()` and no access control on ERC-20 transfers to it. This is structurally identical to the TREC-3 pattern where the `TransferReceiver`'s balance — inflatable by anyone sending WETH to it directly — was used unchecked to determine how much value entered the Rewards accounting.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol`, the predispatch branch of `placeOrder`: [1](#0-0) 

reads `uint256 balance = IERC20(token).balanceOf(dispatcher)` with no snapshot of what the dispatcher held *before* this specific predispatch call, and reverts only if `balance < requiredAmount`. It then builds a sweep call that transfers the *entire* `balance` (not just `requiredAmount`) back to the gateway: [2](#0-1) 

The measured amount is written back into `order.inputs[i].amount`, which subsequently determines the fee-adjusted `reducedInputs[i].amount` credited to escrow: [3](#0-2) 

`_params.dispatcher` is a single fixed, permissionless, address shared across every order placed through the gateway (and across other apps using the same `CallDispatcher`): [4](#0-3) 

Because `CallDispatcher` has an unrestricted `receive()` and accepts ERC-20 `transfer()` from anyone with no owner/allowlist check, any unprivileged party can pre-fund the dispatcher with tokens or ETH out-of-band, immediately before or after another user's `placeOrder` transaction. The `balanceOf(dispatcher)` reading used by the very next `placeOrder` call that exercises the predispatch path cannot distinguish "output produced by this order's own predispatch swap" from "tokens that happened to already be sitting in the shared dispatcher," exactly the flaw the TREC-3 report describes for balance-based reward/allowance accounting. The identical pattern (raw `balanceOf(dispatcher)`/`.balance` read, no per-call before/after delta) exists in the Tron port as well: [5](#0-4) 

### Impact Explanation
Because the amount swept from the dispatcher becomes the committed escrow amount (`_orders[commitment][token]`), which underwrites the order's on-chain commitment hash and later fill/redemption accounting, this allows:
- Permanent loss of any funds accidentally or maliciously sent directly to the shared `CallDispatcher` — they are irrevocably absorbed by whichever order's predispatch sweep next executes, either credited to that unrelated order's escrow or emitted as protocol "dust" (`DustCollected`) that only governance can later sweep, with no path back to the original sender.
- An order placer whose predispatch swap under-delivers (e.g., due to intentionally adverse slippage/MEV) can still have `order.inputs[i].amount` satisfied up to `requiredAmount` using stray balance already sitting in the shared dispatcher that was not contributed by that placer, breaking the invariant that escrowed value originates solely from the order's own declared inputs.

This is a fund-safety/accounting-integrity break reachable by any unprivileged address that can send an ERC-20 transfer or plain ETH transfer to a well-known, permissionless contract address, and it can result in concrete loss of funds for third parties and unbacked escrow crediting for orders.

### Likelihood Explanation
High reachability, no privilege required: `CallDispatcher`'s address is public (used across multiple apps and documented), and reaching it only requires a plain ERC-20 `transfer` or native ETH send — no special timing, no reentrancy, and no dependency on gateway internals. Any user placing an order through the predispatch path is affected any time a third party (attacker or accident) has deposited funds into the dispatcher beforehand.

### Recommendation
Snapshot the dispatcher's (or gateway's) relevant balance *immediately before* dispatching the predispatch call, and compute the "received" amount strictly as `balanceAfter - balanceBefore`, exactly as is already correctly done for the gateway-side measurement (`balancesBefore[i]` / `received = IERC20(token).balanceOf(address(this)) - balancesBefore[i]`). Do this for the dispatcher-side balance as well, so a pre-existing/donated balance is never counted as output of the current predispatch call. Apply the same fix to the Tron variant. Additionally, consider giving `CallDispatcher` an access-controlled sweep/rescue function for unsolicited deposits so they are not silently absorbed into unrelated orders.

### Proof of Concept
1. `CallDispatcher` is deployed once and shared by `IntentGatewayV2` (and other apps) at a fixed, publicly known address (`evm/src/utils/CallDispatcher.sol`, `receive() external payable {}`, no access control on inbound ERC-20 transfers).
2. Attacker (or any unrelated party) sends `X` tokens directly to `CallDispatcher` via a plain `token.transfer(dispatcher, X)` call — no interaction with `IntentGatewayV2` needed.
3. A user then calls `placeOrder` with a predispatch swap that legitimately produces less than `requiredAmount` (e.g., due to slippage) for that same token.
4. In `placeOrder`, `uint256 balance = IERC20(token).balanceOf(dispatcher)` (`evm/src/apps/IntentGatewayV2.sol:274`) now includes the attacker's donated `X`, passing the `balance >= requiredAmount` check that would otherwise fail.
5. The sweep call transfers the entire `balance` (donated funds included) to the gateway, and `order.inputs[i].amount`/`reducedInputs[i].amount` is credited to escrow (`evm/src/apps/IntentGatewayV2.sol:363-368`) as if it were fully produced by the order's own predispatch call — the donor's `X` tokens are consumed with no recourse, and the order settles using value it did not itself provide.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L260-282)
```text
            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L289-306)
```text
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L363-373)
```text
        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/utils/CallDispatcher.sol (L36-62)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-441)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
```
