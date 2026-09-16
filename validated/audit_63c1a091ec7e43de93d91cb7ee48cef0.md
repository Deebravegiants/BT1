## Finding: Unauthenticated `CallDispatcher.dispatch()` Permits Anyone to Drain Stranded Token/ETH Balances

The reported TUSD bug's root cause was a **permissionless function that could move an arbitrary token's balance out of a contract whose accounting depends on that balance staying put**, reachable by literally anyone. Hyperbridge's `CallDispatcher` has the same structural flaw.

### Title
Unauthenticated `dispatch()` on the shared `CallDispatcher` lets anyone drain any stranded token/native balance it holds - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` has no access control at all — it is a plain `external` function with no `onlyGateway`/`onlyHost` modifier — and the contract also has a permissionless payable `receive()`. It is deployed once and shared across an entire `IntentGatewayV2`/`HyperFungibleToken` deployment. Any balance that ends up sitting in this contract between transactions (tokens sent directly to it, or output-call side effects not enumerated in an order's declared assets) is trivially drainable by any unprivileged address, exactly like TUSD's `sweepToken` could be called by anyone to move the CTUSD market's entire underlying balance. [1](#0-0) 

### Finding Description
`CallDispatcher` is intentionally a thin, stateless relay used by `IntentGatewayV2` (predispatch/postdispatch calldata) and by `HyperFungibleToken`/`WrappedHyperFungibleToken` (calldata execution on receive) to route arbitrary `Call[]` batches on behalf of order placers and cross-chain messages: [2](#0-1) 

Its `dispatch(bytes memory encoded)` function decodes a `Call[]` and executes each call — with `to.call{value: call.value}(call.data)` — with **no restriction on who may invoke it**: [3](#0-2) 

The dispatcher is deployed as a single shared instance per gateway/HFT deployment (not per-order), per the deployment scripts: [4](#0-3) [5](#0-4) 

`IntentGatewayV2.placeOrder` and `IntentsBase._execute` rely on this shared dispatcher holding funds only transiently within a single atomic transaction, then sweeping its *entire* `balanceOf`/`.balance` back to the gateway: [6](#0-5) [7](#0-6) 

Critically, the postdispatch sweep in `_execute` only iterates over `order.output.assets` (`outputsLen`) — any token balance the dispatcher acquires as a side effect of the executed calldata that is **not** in that explicit asset list is never swept back and is left stranded in the dispatcher indefinitely. Likewise, `receive() external payable {}` lets anyone push native ETH into the dispatcher outside of any order flow. Because `dispatch()` has no caller restriction, this stranded balance — regardless of how it got there — is retrievable by *any* unprivileged address at any later time, simply by submitting their own `Call[]` (e.g., an ERC-20 `transfer` to themselves) directly to the dispatcher.

This mirrors the TUSD root cause precisely: a balance-moving entry point with no authorization check, reachable by an unprivileged caller, operating on a shared pool of value whose ownership the rest of the protocol's accounting implicitly assumes is safe.

### Impact Explanation
Any token or native ETH balance left in the shared `CallDispatcher` — from calldata side effects not covered by `order.output.assets`, from user error (direct transfers), or from any other integration that references the dispatcher's address as a `to`/beneficiary — is permanently and trivially stealable by an unprivileged third party. Because the dispatcher is shared across *every* order and every `HyperFungibleToken`/`WrappedHyperFungibleToken` message routed through it on that chain, the blast radius is protocol-wide rather than scoped to a single order, and the loss is a direct, irreversible transfer of funds to the attacker — a concrete theft of funds.

### Likelihood Explanation
Exploitation requires no special privilege, no governance action, and no cross-chain proof — only that the dispatcher hold some balance it wasn't fully credited/swept for, which the `_execute` sweep logic (limited to `order.output.assets`) does not guarantee for arbitrary calldata side effects, and which the unrestricted `receive()` guarantees is always possible for native ETH accidentally or deliberately sent to it.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by its configured owner(s) (the specific `IntentGatewayV2`/`HyperFungibleToken` instance(s) it is wired to), or make the dispatcher single-use/ephemeral per order so it cannot accumulate cross-transaction balance. Additionally, broaden `_execute`'s post-call sweep to cover any token balance the dispatcher holds after executing arbitrary calldata, not just the tokens declared in `order.output.assets`, and consider removing or gating the permissionless `receive()`.

### Proof of Concept
1. Any user has, at some prior point, had calldata executed through the shared `CallDispatcher` that resulted in it holding a token not listed in that order's `output.assets` (e.g., a reward/airdrop token emitted by a DEX swap target), or sent ETH directly to the dispatcher's address.
2. An unrelated attacker observes (via a block explorer) that `CallDispatcher` now holds a nonzero balance of that token/ETH.
3. The attacker calls `CallDispatcher.dispatch(abi.encode(calls))` directly, where `calls` is a single `Call{ to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance) }` (or, for native ETH, `Call{ to: attacker, value: balance, data: "" }`).
4. Since `dispatch()` performs no caller check, the call succeeds and the attacker receives the full stranded balance.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L17-62)
```text
import {ICallDispatcher, Call} from "@hyperbridge/core/interfaces/ICallDispatcher.sol";

/**
 * @title The CallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This contract is used to dispatch calls to other contracts.
 */
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

**File:** evm/script/DeployHFT.s.sol (L9-26)
```text
contract DeployHFT is BaseScript {
    function deploy() internal override {
        string memory name = vm.envString("HFT_NAME");
        string memory symbol = vm.envString("HFT_SYMBOL");

        CallDispatcher dispatcher = new CallDispatcher{salt: salt}();
        HyperFungibleToken hft = new HyperFungibleToken{salt: salt}(name, symbol, admin);

        hft.configure(HyperFungibleToken.ConfigOptions({
            host: HOST_ADDRESS,
            dispatcher: address(dispatcher)
        }));

        vm.stopBroadcast();
        console.log("=== HFT Deployment ===");
        console.log("HyperFungibleToken:", address(hft));
        console.log("CallDispatcher:", address(dispatcher));
    }
```

**File:** evm/script/DeployWrappedHFT.s.sol (L9-30)
```text
contract DeployWrappedHFT is BaseScript {
    function deploy() internal override {
        address underlying = vm.envAddress("UNDERLYING");
        bool isWeth = vm.envBool("IS_WETH");

        CallDispatcher dispatcher = new CallDispatcher{salt: salt}();
        WrappedHyperFungibleToken whft = new WrappedHyperFungibleToken{salt: salt}(admin);

        whft.configure(WrappedHyperFungibleToken.WrappedConfigOptions({
            host: HOST_ADDRESS,
            dispatcher: address(dispatcher),
            underlying: underlying,
            isWeth: isWeth
        }));

        vm.stopBroadcast();
        console.log("=== WrappedHFT Deployment ===");
        console.log("WrappedHyperFungibleToken:", address(whft));
        console.log("CallDispatcher:", address(dispatcher));
        console.log("Underlying:", underlying);
        console.log("IsWETH:", isWeth);
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L258-303)
```text
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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

                unchecked {
                    ++i;
                }
            }

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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-545)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }

        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
        }
    }
```
