### Title
`Params.priceOracle` in `IntentGatewayV2` can desync from `VWAPOracle._intentGateway`, permanently freezing spread recording / order fills - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/utils/VWAPOracle.sol`)

### Summary
`IntentsBase._params.priceOracle` is a mutable field that governance can repoint to any `VWAPOracle` contract via `_updateParams`, while the `VWAPOracle` on the other side stores its gateway reference (`_intentGateway`) once, at construction, with no way to update it later. If the two are ever repointed independently — the exact "MultiStrategy/Multipool" desync pattern from the source report — the oracle rejects the gateway that is now configured to call it, because its access-control check trusts a different, stale gateway address.

### Finding Description
`IntentsBase._params` holds `priceOracle`, validated only for having code (`evm/src/apps/intentsv2/IntentsBase.sol` `_validateParams`, lines 592-598) and freely replaced through governance's `_updateParams` (lines 611-628): [1](#0-0) [2](#0-1) 

On the other side, `VWAPOracle` stores the gateway it trusts in `_intentGateway`, set once in the constructor with no setter at all: [3](#0-2) 

`recordSpread`, the only entry point the gateway calls on the oracle after a fill, is gated purely by that stale, unilaterally-fixed address: [4](#0-3) 

This mirrors the report's root cause precisely: one side of a mutually-referencing pair (`Multipool.strategy` / `IntentGatewayV2._params.priceOracle`) is freely mutable, while the other side (`MultiStrategy.multipool` / `VWAPOracle._intentGateway`) is fixed and never re-synchronized when the mutable side changes. Because neither `_validateParams` nor `_updateParams` checks that the incoming `priceOracle`'s own `_intentGateway` equals `address(this)`, governance can (accidentally, through a redeploy or a copy-paste of the wrong oracle address — no malicious intent required) set `_params.priceOracle` to an oracle instance whose `_intentGateway` points at a different or previous gateway deployment.

### Impact Explanation
Once desynced, every call the gateway makes to `recordSpread` on that oracle reverts with `Unauthorized`, since `msg.sender` (the current gateway) no longer equals the address baked into the oracle at construction. Because there is no setter to fix `_intentGateway` after deployment, the desync is permanent for that oracle instance — the only remedy is another governance-driven `_updateParams` call away from that oracle (or an oracle redeploy), rather than a lightweight fix. If the fill-side code path is not defensively wrapped, the revert propagates and blocks legitimate, permissionless order fills that would otherwise call into pricing/spread accounting, which fits the "route unable to deliver" criterion. Given the difficulty of independently locating the exact fill call site in this pass, I could not directly confirm whether `_execute`/fill flow wraps this call in a try/catch — this is a real gap in verification and should be checked directly in the repository (e.g. by grepping `recordSpread(` in `IntentGatewayV2.sol`) before treating this as fully proven.

### Likelihood Explanation
The desync requires only an ordinary governance action (`UpdateParams`) pointing `priceOracle` at an oracle whose `_intentGateway` was fixed to a different address — no attacker privilege escalation is needed, and nothing in `_validateParams` prevents it. This is analogous to redeploying/rotating a strategy contract in the original report: a routine operational action, not a malicious one, is enough to trigger the state desync.

### Recommendation
Add a two-way binding check in `_validateParams` (or `_updateParams`) that requires `IIntentPriceOracle(update.params.priceOracle).intentGateway() == address(this)` before accepting a new `priceOracle`, mirroring the report's suggested fix of only allowing the pointer to be set when currently unset/matching. Alternatively, give `VWAPOracle` an admin-gated, one-shot-per-gateway-rotation `setIntentGateway` function that must be called in the same governance action that updates `_params.priceOracle`, and revert the gateway update if the oracle side isn't updated atomically.

### Proof of Concept
1. Deploy `IntentGatewayV2` (gateway A) and `VWAPOracle` constructed with `intentGateway = address(gatewayA)`.
2. Governance dispatches `UpdateParams` on gateway A's twin, a newly upgraded/rotated `IntentGatewayV2` (gateway B, e.g. after a proxy migration or redeployment), setting `_params.priceOracle` to the same `VWAPOracle` instance (still bound to gateway A).
3. `_validateParams` passes because it only checks `priceOracle.code.length != 0`; the update commits.
4. A solver fills an order on gateway B; the fill path calls `VWAPOracle.recordSpread(...)`.
5. `recordSpread`'s `restrict(_intentGateway)` modifier checks `msg.sender == address(gatewayA)`, but `msg.sender` is gateway B — the call reverts with `Unauthorized`, and (pending confirmation of the exact call site's error handling) this can block fill completion, freezing user funds mid-fill or leaving spread accounting permanently broken for that oracle.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L592-598)
```text
    function _validateParams(Params memory p) internal view {
        if (p.host == address(0) || p.host.code.length == 0) revert InvalidInput();
        if (p.dispatcher == address(0) || p.dispatcher.code.length == 0) revert InvalidInput();
        if (p.surplusShareBps > 10_000) revert InvalidInput();
        if (p.protocolFeeBps >= 10_000) revert InvalidInput();
        if (p.priceOracle != address(0) && p.priceOracle.code.length == 0) revert InvalidInput();
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L611-616)
```text
    function _updateParams(ParamsUpdate memory update) internal {
        _validateParams(update.params);

        emit ParamsUpdated({previous: _params, current: update.params});
        _params = update.params;

```

**File:** evm/src/utils/VWAPOracle.sol (L90-121)
```text
    /**
     * @dev Address for the intent gateway contract
     */
    address public _intentGateway;

    /**
     * @dev Mapping from (sourceChainHash, token) => decimals for remote source chain tokens
     * @dev Destination chain token decimals are read directly from IERC20Metadata.decimals()
     */
    mapping(bytes32 => mapping(address => uint8)) private _tokenDecimals;

    /**
     * @dev Mapping from (sourceChainHash, token) => cumulative spread data
     */
    mapping(bytes32 => mapping(address => CumulativeSpreadData)) private _tokenSpreads;

    /// @notice Thrown when an unauthorized action is attempted
    error Unauthorized();

    /// @notice Thrown when invalid input is provided
    error InvalidInput();

    // restricts call to the provided `caller`
    modifier restrict(address caller) {
        if (_msgSender() != caller) revert Unauthorized();
        _;
    }

    constructor(address admin, address intentGateway) {
        _admin = admin;
        _intentGateway = intentGateway;
    }
```

**File:** evm/src/utils/VWAPOracle.sol (L167-176)
```text
    /**
     * @inheritdoc IIntentPriceOracle
     */
    function recordSpread(
        bytes32 commitment,
        bytes memory sourceChain,
        TokenInfo[] calldata inputs,
        TokenInfo[] calldata outputs
    ) external restrict(_intentGateway) {
        // Validate inputs and outputs have the same length
```
