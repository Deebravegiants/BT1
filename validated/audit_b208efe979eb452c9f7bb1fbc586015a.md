### Title
Missing bounds validation on `_params.protocolFeeBps` / `_params.surplusShareBps` in Tron `IntentGatewayV2.setParams` allows escrow-accounting corruption and solver-fillable DoS/fund-freezing - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The mainline EVM `IntentGatewayV2` (`evm/src/apps/intentsv2/IntentsBase.sol`) enforces that `surplusShareBps <= 10_000` and `protocolFeeBps < 10_000` via `_validateParams`, called from both `initialize`/`setParams` and the cross-chain `_updateParams` governance path. [1](#0-0) 
The Tron port of the same contract implements its own `setParams` that stores the admin-supplied `Params` struct directly with **no validation at all**: [2](#0-1) 
This mirrors the reported bug class exactly: a state variable ("`negativeRewardThreshold` must be negative", here "`protocolFeeBps` must be < 10000 / `surplusShareBps` must be <= 10000") that is documented/relied-upon to stay within an invariant range, but the setter performs no `require`/revert check before accepting caller-supplied values.

### Finding Description
On Tron, `_params.protocolFeeBps` and `_params.surplusShareBps` are consumed unchecked in the unprivileged, user/solver-triggered `placeOrder` and fill/surplus-splitting paths:

- In `placeOrder`, the protocol fee is computed as `protocolFee = (originalAmount * protocolFeeBps) / 10_000; reducedAmount = originalAmount - protocolFee;`. [3](#0-2) 
If `protocolFeeBps` is ever set to `>= 10_000` (no cap enforced by `setParams`), `protocolFee` can equal or exceed `originalAmount`, causing `reducedAmount = originalAmount - protocolFee` to underflow and revert (Solidity 0.8 checked arithmetic), bricking `placeOrder` for every user attempting to escrow that input token — a permanent denial-of-service on order placement reachable by any ordinary user.
- The same class of unchecked basis-points value is used for surplus splitting (`_splitSurplus` in the shared `IntentsBase.sol`, which the Tron file also relies on architecturally): `protocolShare = (dust * surplusShareBps) / 10_000; beneficiaryShare = dust - protocolShare;`. [4](#0-3) 
A `surplusShareBps > 10_000` makes `protocolShare > dust`, so `beneficiaryShare = dust - protocolShare` underflows and reverts, bricking `fillOrder` for any solver attempting to fill an order with surplus — again reachable by an unprivileged intent solver.

Because Tron's `setParams` (unlike the audited EVM `_validateParams`) has no bound check, a single misconfigured (not necessarily malicious — just unvalidated) admin call permanently locks out the unprivileged `placeOrder`/`fillOrder` flows that every user and solver depends on, and any escrow already created before the bad value is set may become permanently unfillable/uncancelable if downstream fee math on the same commitment reverts.

### Impact Explanation
This qualifies as Medium-to-High: it can permanently freeze/brick the two most fundamental unprivileged entry points of the Intent Gateway (`placeOrder` for users, `fillOrder`/surplus-splitting for solvers) once an out-of-range `protocolFeeBps`/`surplusShareBps` value is stored, with no path to recovery other than a further privileged `setParams`/governance update — meeting the "permanent freezing of funds"/"route unable to deliver" bar (escrowed inputs placed under a still-valid but broken configuration cannot be filled). It also diverges from the security invariant that the sibling EVM contract explicitly enforces, showing the Tron port dropped a validated safety check present elsewhere in the same protocol.

### Likelihood Explanation
Likelihood is moderate: `setParams` is only privileged (msg.sender == admin, one-time before `_admin` is zeroed) or via governance in the sibling `_updateParams` flow, so triggering the bug requires a governance/config mistake rather than attacker control. However, unlike the mainline `IntentsBase._validateParams`, which the team clearly considered necessary and implemented, the Tron variant has zero defense-in-depth against exactly this configuration error, making an operational slip (e.g., copying a bps value expressed in a different base, or a decimal/percentage unit confusion) sufficient to trigger a protocol-wide DoS reachable by every ordinary user/solver thereafter.

### Recommendation
Add the same validation that `IntentsBase._validateParams` performs to the Tron `IntentGatewayV2.setParams` (and any Tron-side `updateParams`/governance path) before persisting `_params`:
```solidity
function setParams(Params memory p) public {
    if (msg.sender != _admin) revert Unauthorized();
    if (p.surplusShareBps > 10_000) revert InvalidInput();
    if (p.protocolFeeBps >= 10_000) revert InvalidInput();
    _admin = address(0);
    _params = p;
}
```
Also validate `destinationFeeBps` overrides on the Tron contract the same way `IntentsBase._updateParams` does (`feeBps >= 10_000 → revert`), since a per-destination override bypasses the top-level `protocolFeeBps` and would reproduce the same underflow independently.

### Proof of Concept
1. Deploy Tron `IntentGatewayV2` and call `initialize`/`setParams` (as `_admin`) with `Params.protocolFeeBps = 10_000` (or higher) — this succeeds because `setParams` performs no bounds check. [2](#0-1) 
2. Any user calls `placeOrder` with a nonzero input amount for a destination without a distinct `destinationFeeBps` override (so `protocolFeeBps` from `_params` is used). [5](#0-4) 
3. `protocolFee = originalAmount * 10_000 / 10_000 = originalAmount`, so `reducedAmount = originalAmount - protocolFee = 0` (or reverts on underflow for any `protocolFeeBps > 10_000`) — `placeOrder` reverts or produces zero-value/broken orders for every caller, permanently denying the core user-facing flow until a further privileged fix is applied.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L426-434)
```text
    function _splitSurplus(uint256 dust, bool hasOutputCall)
        internal
        view
        returns (uint256 protocolShare, uint256 beneficiaryShare)
    {
        if (hasOutputCall) return (dust, 0);
        protocolShare = (dust * _params.surplusShareBps) / 10_000;
        beneficiaryShare = dust - protocolShare;
    }
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L306-311)
```text
    function setParams(Params memory p) public {
        if (msg.sender != _admin) revert Unauthorized();

        _admin = address(0);
        _params = p;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L350-364)
```text
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
```
