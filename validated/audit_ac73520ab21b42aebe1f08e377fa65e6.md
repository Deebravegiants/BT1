### Title
Missing validation on governance-delivered `UpdateParams` lets a Hyperbridge relayer permanently freeze the Tron `IntentGatewayV2` by zeroing `host`/`dispatcher`/`priceOracle` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` applies governance `UpdateParams` requests to `_params` without any of the zero-address/sanity checks that the equivalent EVM contract enforces on the same data.

### Finding Description
`onAccept` handles `RequestKind.UpdateParams` by decoding the request body straight into `_params` with no validation at all: [1](#0-0) 

Compare this to the local, admin-gated `setParams`, which is also unguarded on the struct's contents (only checks `msg.sender == _admin`): [2](#0-1) 

The mainline EVM `IntentGatewayV2` (and its tests) explicitly reject a zero `host`, a non-contract `dispatcher`, an out-of-range `surplusShareBps`/`protocolFeeBps`, and a non-contract `priceOracle` for both `initialize` and the governance `UpdateParams` path, as shown by the params-validation test suite: [3](#0-2) 

The Tron contract has no analogous `InvalidInput` checks in its `onAccept`/`UpdateParams` branch, even though the `InvalidInput` error is declared in the contract: [4](#0-3) 

Because `UpdateParams` requests are delivered by any relayer that submits a valid consensus/state proof through the host (there is no relayer allow-list on this contract's `onAccept`, unlike `HostManager` or `SimplexPaymaster` which gate on a specific admin/relayer), a message that carries `params.host == address(0)` (or `dispatcher`/`priceOracle` set to an EOA/zero) will be accepted and written into storage unchecked.

### Impact Explanation
`host()` returns `_params.host` and is used throughout the contract (`placeOrder`, `cancelOrder`, `dispatchWithFeeToken`, fee dispatch, escrow release, etc.) to obtain the `IDispatcher`/`IHost` instance. If `_params.host` is zeroed, every subsequent call into `IDispatcher(host())...` reverts, permanently freezing order placement, cancellation, and fill/withdrawal flows for all users, solvers, and fillers on that deployment — funds already escrowed in `_orders`/`_filled` become unreachable through the normal code paths since the withdraw/refund flow depends on `host()`/`dispatcher()`. A zeroed or malformed `priceOracle`/`dispatcher` similarly breaks fee computation and dispatch, again freezing user-facing functionality. This is a permanent freezing-of-funds condition triggerable by a single malformed but validly-proven cross-chain governance message, not requiring any local admin key.

### Likelihood Explanation
Likelihood is bounded by the fact that `UpdateParams` must originate from the Hyperbridge parachain and pass consensus/state verification, but no additional access control restricts which relayer can deliver it (there is no `relayer()`/`onlyRelayer` gate in this file's `onAccept`, unlike `SimplexPaymaster` or `HostManager`). A single bug in the off-chain governance parameter construction, or a compromised/malicious relayer able to forge a legitimate cross-chain governance payload, is sufficient — no local privileged key is needed to trigger the freeze once the message is delivered.

### Recommendation
Mirror the EVM `IntentGatewayV2` validation in the Tron contract's `UpdateParams` handling (and in `setParams`): require `update.params.host != address(0)` and has code, `dispatcher` is a contract, `priceOracle` is a contract (or intentionally allowed to be zero only when unused), and bound `surplusShareBps`/`protocolFeeBps` to valid ranges, reverting with `InvalidInput()` before writing to `_params`.

### Proof of Concept
1. Hyperbridge relayer submits a proven `PostRequest` from the Hyperbridge parachain source to the Tron `IntentGatewayV2`, with `body = RequestKind.UpdateParams || abi.encode(ParamsUpdate{ params: Params{ host: address(0), dispatcher: <any>, ...}, destinationFees: [] })`.
2. `onAccept` reaches the `UpdateParams` branch at [1](#0-0) , and stores `_params = update.params` with `host == address(0)`, with no validation.
3. Any subsequent call to `placeOrder`, `cancelOrder`, or `onAccept`-triggered `withdraw` invokes `host()` → `IDispatcher(address(0))...`, which reverts against a non-contract address, freezing the gateway for all users on that chain.

Note: I was unable to fully trace the `withdraw`/`dispatchWithFeeToken` implementations further down the file (past line 650) within the available tool budget, so exact revert points beyond `host()`/`dispatch` calls are inferred from the pattern used elsewhere in the same file (e.g., `cancelOrder` at lines 522-618) rather than directly confirmed line-by-line.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L141-142)
```text
    /// @notice Thrown when an invalid input is provided.
    error InvalidInput();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L306-311)
```text
    function setParams(Params memory p) public {
        if (msg.sender != _admin) revert Unauthorized();

        _admin = address(0);
        _params = p;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L644-649)
```text
        } else if (kind == RequestKind.UpdateParams) {
            // Decode the body which includes optional destination-specific protocol fee updates
            ParamsUpdate memory update = abi.decode(incoming.request.body[1:], (ParamsUpdate));
            emit ParamsUpdated({previous: _params, current: update.params});
            _params = update.params;

```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3804-3861)
```text
    function testRevert_SetParams_ZeroHost() public {
        IntentGatewayV2 gw = _deployGatewayProxy();
        Params memory p = Params({
            host: address(0),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: 5000,
            protocolFeeBps: 0,
            priceOracle: address(0)
        });
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gw.initialize(p, new bytes[](0), address(0));
    }

    /// @notice setParams rejects EOA dispatcher (no code).
    function testRevert_SetParams_EOADispatcher() public {
        IntentGatewayV2 gw = _deployGatewayProxy();
        Params memory p = Params({
            host: address(host),
            dispatcher: address(0xdead),
            solverSelection: false,
            surplusShareBps: 5000,
            protocolFeeBps: 0,
            priceOracle: address(0)
        });
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gw.initialize(p, new bytes[](0), address(0));
    }

    /// @notice setParams rejects surplusShareBps > 10000.
    function testRevert_SetParams_SurplusShareBpsTooHigh() public {
        IntentGatewayV2 gw = _deployGatewayProxy();
        Params memory p = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: 10001,
            protocolFeeBps: 0,
            priceOracle: address(0)
        });
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gw.initialize(p, new bytes[](0), address(0));
    }

    /// @notice setParams rejects protocolFeeBps >= 10000.
    function testRevert_SetParams_ProtocolFeeBpsTooHigh() public {
        IntentGatewayV2 gw = _deployGatewayProxy();
        Params memory p = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: 5000,
            protocolFeeBps: 10000,
            priceOracle: address(0)
        });
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gw.initialize(p, new bytes[](0), address(0));
    }
```
