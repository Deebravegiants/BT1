Based on my investigation, EvmHost's `withdraw()` function operates on the host contract's own balance [1](#0-0) , and the HostManager delegates the `Withdraw` governance action directly to `IHostManager(_params.host).withdraw(withdrawParams)` [2](#0-1) . HostManager itself has no function to move ETH out of its own balance — governance withdrawals only ever pull from the `EvmHost` contract's balance, never from `HostManager`'s. Yet `HostManager` still exposes a `receive() external payable {}` with a comment explicitly warning "Do not send any tokens directly to this contract" [3](#0-2) . This is a real permanent-freezing analog matching the reported bug class, and I can confidently produce a finding.

### Title
Unnecessary/dangerous `receive()` on `HostManager` permanently traps any ETH sent to it - (File: `evm/src/core/HostManager.sol`)

### Summary
`HostManager` accepts arbitrary native ETH via an unconditional `receive()` function, but it has no `withdraw`, `sweep`, or `rescue` function of its own. The only withdrawal path exposed by `HostManager.onAccept` (the `Withdraw` governance action) forwards the call to `IHostManager(_params.host).withdraw(...)`, which operates on `EvmHost`'s own balance — not `HostManager`'s. Any ETH that lands in `HostManager` (accidental transfer, dust from a future integration, a misconfigured relayer/fee flow, etc.) is permanently stuck with no code path to recover it.

### Finding Description
`HostManager` declares:
```solidity
/*
 * @dev fallback function for tests. Do not send any tokens directly to this contract.
 */
receive() external payable {}
``` [3](#0-2) 

The comment itself acknowledges the contract should never hold value, which is a strong signal that `receive()` should not exist in production, exactly mirroring the reported "Unnecessary `receive()`" bug class (functions that needlessly widen the surface for value to become trapped).

Crucially, unlike `EvmHost` — whose own `receive()` is paired with a `withdraw()` function that lets governance retrieve the host's native balance — `HostManager`'s governance `Withdraw` action does not touch `HostManager`'s own balance at all:
```solidity
if (action == OnAcceptActions.Withdraw) {
    // This is where governance & relayers can withdraw their revenue.
    WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
    IHostManager(_params.host).withdraw(withdrawParams);
}
``` [2](#0-1) 

This calls `withdraw` on `_params.host` (the `EvmHost` contract), pulling from the host's balance/fee-token accounting, not from `HostManager` itself. There is no `SetHostParam`, `SetAdmin`, or any other `OnAcceptActions` variant, nor any other public/external function in `HostManager`, that moves ETH out of the contract. Once ETH lands in `HostManager` via `receive()`, it is permanently locked — no admin, no governance action, and no future `SetAdmin`/`SetHostParam` request can move it out, since none of those code paths reference `address(this).balance`.

### Impact Explanation
Any native ETH sent to `HostManager` (by mistake, by a future protocol wiring change, or by anyone who resolves the contract address expecting it to behave like `EvmHost`) is permanently frozen with zero recovery path — a concrete case of permanent freezing of funds. `HostManager` is a governance-critical contract deployed per chain to relay Hyperbridge governance actions (fee/host-param updates, admin rotation), so it is a plausible target for accidental or intentional value transfers (e.g., a user manually calling a "withdraw"-style flow against the wrong address, or a future integration assuming parity with `EvmHost`'s dust-collection semantics).

### Likelihood Explanation
Likelihood is moderate: the contract explicitly documents that it should never receive tokens, which suggests it wasn't intended to hold funds, yet the unconditional `receive()` remains reachable by any unprivileged sender with a single plain ETH transfer — no proof, extrinsic, or relayer role is needed to trigger the freeze. The trigger event (someone or something sending ETH there) is plausible but not adversarially exploitable for profit; it's a self-inflicted or accidental freeze rather than an attacker directly stealing funds.

### Recommendation
Remove the `receive() external payable {}` function from `HostManager` entirely, since the contract's design (per its own comment) never expects to hold native tokens and its governance actions never reference `address(this).balance`. If native ETH must ever be supported for a future use case, pair the `receive()` with an explicit governance-gated sweep/withdraw function that transfers `address(this).balance` to a beneficiary, mirroring `EvmHost.withdraw`.

### Proof of Concept
1. Deploy `HostManager` per the existing constructor/`init` flow.
2. Any account (no special privileges required) sends ETH directly to the `HostManager` contract address, e.g. `hostManager.call{value: 1 ether}("")` — this succeeds because of the unconditional `receive()` at [3](#0-2) .
3. Attempt to recover the funds:
   - Deliver a `Withdraw` `onAccept` action — it calls `IHostManager(_params.host).withdraw(...)`, which only affects `EvmHost`'s balance, not `HostManager`'s [2](#0-1) .
   - Deliver `SetHostParam` or `SetAdmin` — neither touches `address(this).balance`.
4. Confirm `address(hostManager).balance` remains unchanged at 1 ether indefinitely — the ETH is permanently unrecoverable through any function in the contract.

### Citations

**File:** evm/src/core/EvmHost.sol (L383-386)
```text
    /*
     * @dev receive function for UniswapV2Router02, collects all dust native tokens.
     */
    receive() external payable {}
```

**File:** evm/src/core/HostManager.sol (L83-86)
```text
    /*
     * @dev fallback function for tests. Do not send any tokens directly to this contract.
     */
    receive() external payable {}
```

**File:** evm/src/core/HostManager.sol (L144-148)
```text
        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
```
