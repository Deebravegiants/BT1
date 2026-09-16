### Title
`EvmHost` accepts a zero `uniswapV2` router address, but validates the other config addresses - (File: `evm/src/core/EvmHost.sol`)

### Summary
`HostParams.uniswapV2` (the local `UniswapV2Router02` address used to swap the chain's native token to the ISMP fee token) is never checked against `address(0)` when it is applied via `initialize`/`updateHostParamsInternal`, while the three sibling configuration addresses (`hostManager`, `handler`, `consensusClient`) are each guarded by a dedicated revert.

### Finding Description
`HostParams` declares `uniswapV2` as "the local `UniswapV2Router02` contract, used for swapping the native token to the feeToken" [1](#0-0) . `EvmHost` defines explicit sanity-check errors for the other externally-supplied addresses in `HostParams`: `InvalidHostManager`, `InvalidHandler`, and `InvalidConsensusClient`, each documented as firing "if the address was zero, not a contract, or didn't meet its required ERC165 interface" [2](#0-1) . No equivalent `InvalidUniswapV2`/zero-check error exists for `uniswapV2` anywhere in the error list or in `initialize`/`updateHostParamsInternal`.

This omission is empirically confirmed by the test fixtures themselves, which construct a live `TestHost`/`EvmHost` with `uniswapV2: address(0)` and complete construction/initialization without any revert: [3](#0-2) 

The `receive()` fallback is explicitly documented as existing "for UniswapV2Router02, collects all dust native tokens," confirming the router is invoked as an external contract in the host's native-fee-payment flow [4](#0-3) . This is structurally the same bug class as the external report: a swap-router-type address (`UniV2SwapRouter`) is stored without a zero-address sanity check, even though sibling addresses in the same configuration struct are checked.

### Impact Explanation
If `uniswapV2` is ever set (or left) as `address(0)` — via the initial `initialize` call or a later `hostManager`/admin `updateHostParams` governance action — any code path that calls into the router (e.g., swapping native-token payment into the fee token during dispatch) will revert on every invocation, since `address(0)` has no code. This permanently blocks the native-token dispatch path for that `EvmHost` instance until governance pushes a corrected `HostParams`, i.e., a route becomes unable to deliver/process messages that rely on native-token fee swapping — matching the "route unable to deliver messages" impact class for a Medium finding.

### Likelihood Explanation
`uniswapV2` is set once at `initialize` (admin-only) and can subsequently be changed only via `hostManager`/`TestnetHost` admin governance calls to `updateHostParams`, so this requires an operational/governance misconfiguration rather than direct attacker control. However, the asymmetry — three of the four externally supplied addresses in the exact same struct are hardened against zero/non-contract values while `uniswapV2` is not — indicates this is an oversight rather than an intentional design choice, making an accidental zero-address deployment or governance update plausible, consistent with the original report's own client-fix precedent (adding the missing zero check).

### Recommendation
Add a zero-address (and ideally ERC165/contract-existence) check for `params.uniswapV2` in `updateHostParamsInternal`/`initialize`, mirroring the existing `InvalidHostManager`, `InvalidHandler`, and `InvalidConsensusClient` guards, e.g. introduce `InvalidUniswapV2` and revert when `params.uniswapV2 == address(0)`.

### Proof of Concept
1. Admin calls `EvmHost.initialize(params)` (or governance later calls `updateHostParams`) with `params.uniswapV2 == address(0)` — this succeeds with no revert, as demonstrated by the existing test setups that construct hosts this way [3](#0-2) .
2. Any subsequent flow that invokes the configured `uniswapV2` router (native-token-to-fee-token swap during dispatch, per the `receive()` doc comment) reverts because `address(0)` has no code [4](#0-3) .
3. Result: the native-fee dispatch path on that host is permanently unusable until a corrected `HostParams` is pushed through governance.

Note: I was unable to locate and inspect the exact function body that performs the `uniswapV2` swap call (only its usage comment and the `HostParams`/error definitions were retrievable within the indexed context), so the precise call site and revert message could not be cited directly; a full-repository session would be needed to pinpoint that function exactly.

### Citations

**File:** evm/src/core/EvmHost.sol (L54-55)
```text
    // The local UniswapV2Router02 contract, used for swapping the native token to the feeToken.
    address uniswapV2;
```

**File:** evm/src/core/EvmHost.sol (L318-325)
```text
    // Host manager address was zero, not a contract or didn't meet it's required ERC165 interface.
    error InvalidHostManager();

    // Handler address was zero, not a contract or didn't meet it's required ERC165 interface.
    error InvalidHandler();

    // Consensus client address was zero, not a contract or didn't meet it's required ERC165 interface.
    error InvalidConsensusClient();
```

**File:** evm/src/core/EvmHost.sol (L383-386)
```text
    /*
     * @dev receive function for UniswapV2Router02, collects all dust native tokens.
     */
    receive() external payable {}
```

**File:** evm/tests/foundry/HandlerV2Test.sol (L61-73)
```text
        HostParams memory params = HostParams({
            uniswapV2: address(0),
            admin: address(this),
            hostManager: address(manager),
            handler: address(handler),
            unStakingPeriod: 21 * (60 * 60 * 24),
            challengePeriod: 0,
            consensusClient: address(consensusClient),
            feeToken: address(feeToken),
            hyperbridge: StateMachine.kusama(paraId),
            stateMachines: stateMachines
        });
        host = new TestHost(params);
```
