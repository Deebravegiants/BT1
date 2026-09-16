### Title
`HostManager.init` binds to a host without verifying the host recognizes it as its `hostManager`, permanently freezing governance withdrawals - (File: evm/src/core/HostManager.sol)

### Summary
`HostManager.init` lets the admin bind the manager to an `EvmHost` address exactly once, but never checks that the target host's `hostParams.hostManager` actually points back to this `HostManager` instance. This mirrors the reported `setNFT` bug: a one-shot setter assigns an external contract dependency without validating that the dependency actually grants this contract the privileged role it needs to function.

### Finding Description
`HostManager.init` is the designated path for binding a manager to a host "when the host is not known at construction": [1](#0-0) 

It is guarded only by `restrict(msg.sender, _params.admin)` and the one-shot `AlreadyInitialized` check — there is no call back into `hostAddr` to confirm `EvmHost.hostParams().hostManager == address(this)`. Once set, `_params.host` can never be changed again (`AlreadyInitialized` on any second call), exactly like `MeritDutchAuction.setNFT`'s "can only be set once" guard with no minter-role validation.

All of the manager's privileged, revenue-critical actions are dispatched through `IHostManager(_params.host)`: [2](#0-1) 

but the corresponding `EvmHost.withdraw` and `EvmHost.updateHostParams` functions are restricted to the caller matching `_hostParams.hostManager` — confirmed by the codebase's own flow documentation: "`EvmHost.updateHostParams`, which is restricted to `_hostParams.hostManager`" [3](#0-2) . If the `hostAddr` passed to `init` does not have this manager registered as its `hostManager` (e.g., wrong address supplied, wrong network, or a host whose `hostManager` param points elsewhere), then every subsequent `IHostManager(_params.host).withdraw(...)` and `.updateHostParams(...)` call made from this manager will revert at the host, because `msg.sender` (this manager) does not match the host's stored `hostManager`.

### Impact Explanation
Because `init` is one-shot and irreversible, an incorrect binding cannot be corrected later — there is no setter to update `_params.host` a second time. This permanently freezes:
- All `Withdraw` governance actions relayed from Hyperbridge through this manager, locking accrued relayer/protocol fee revenue in the host with no path to retrieve it via this manager.
- All `SetHostParam` actions, meaning the host's `HostParams` (including the correct `hostManager`, `handler`, `consensusClient`, etc.) can never be fixed remotely once the wrong manager is bound, since the recovery mechanism itself is broken.

This is a permanent freezing of protocol funds/functionality with no recovery path — matching the report's "nobody can mint" impact class but for governance-controlled fee withdrawal and host parameter updates.

### Likelihood Explanation
`init` is intended precisely for the case where the host isn't known at construction time (per the code's own comment), meaning this is an expected deployment/operational code path, not a hypothetical. A single incorrect address supplied by the admin during this call — or a host whose `HostParams.hostManager` was set to a different address than the one calling `init` — triggers the freeze immediately and irreversibly, with no on-chain validation catching the misconfiguration.

### Recommendation
Have `init` verify the binding is mutual before committing it:
```solidity
function init(address hostAddr) external restrict(msg.sender, _params.admin) {
    if (_params.host != address(0)) revert AlreadyInitialized();
    require(IHost(hostAddr).hostParams().hostManager == address(this), "host does not recognize this manager");
    _params.host = hostAddr;
}
```
This ensures the manager only binds to a host that already designates it as `hostManager`, preventing an unrecoverable freeze of withdrawal and host-param-update governance actions.

### Proof of Concept
1. Deploy `EvmHost` with `HostParams.hostManager = managerB` (some other/future manager address).
2. Deploy a fresh `HostManager` (`managerA`) constructed with `host: address(0)`, per the "host not known at construction" flow.
3. Admin calls `managerA.init(address(host))`. This succeeds because `init` performs no check against `host`'s stored `hostManager`.
4. Hyperbridge later dispatches a `Withdraw` or `SetHostParam` request addressed to `managerA`. `managerA.onAccept` executes `IHostManager(address(host)).withdraw(...)` / `.updateHostParams(...)`.
5. Inside `EvmHost`, the caller-restriction check (`msg.sender == _hostParams.hostManager`) fails because `msg.sender == managerA` but `_hostParams.hostManager == managerB`; the call reverts.
6. Because `managerA` is already initialized, `init` can never be called again (`AlreadyInitialized`), so this mismatch, and the resulting freeze of withdrawals and host param updates, is permanent.

### Citations

**File:** evm/src/core/HostManager.sol (L112-123)
```text
    /**
     * @notice Binds this contract to the ISMP host
     * @dev Exists to seal the cyclic dependency between this contract and the host when the host
     * is not known at construction; a manager constructed with its host set needs no `init`. Only
     * the admin may call it, and only once: the admin is the governance relayer key, and letting it
     * re-point the host later would let that key cut the host off from its own governance.
     * @param hostAddr The host this contract accepts `onAccept` calls from and acts upon
     */
    function init(address hostAddr) external restrict(msg.sender, _params.admin) {
        if (_params.host != address(0)) revert AlreadyInitialized();
        _params.host = hostAddr;
    }
```

**File:** evm/src/core/HostManager.sol (L134-159)
```text
    function onAccept(IncomingPostRequest calldata incoming)
        external
        override
        restrict(msg.sender, _params.host)
        restrict(incoming.relayer, _params.admin)
    {
        PostRequest calldata request = incoming.request;
        // Only the Hyperbridge parachain can send requests to this module.
        if (!request.source.equals(IHost(_params.host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
        } else if (action == OnAcceptActions.SetHostParam) {
            HostParams memory hostParams = abi.decode(request.body[1:], (HostParams));
            IHostManager(_params.host).updateHostParams(hostParams);
        } else if (action == OnAcceptActions.SetAdmin) {
            // Rotates the governance relayer.
            address newAdmin = abi.decode(request.body[1:], (address));
            if (newAdmin == address(0)) revert InvalidAdmin();
            emit AdminUpdated({previous: _params.admin, current: newAdmin});
            _params.admin = newAdmin;
        }
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L24-26)
```markdown
The address checked in step 3 is only as trustworthy as the contract in step 1, and that contract
is `_hostParams.handler`, which `HostManager.onAccept` can replace through a `SetHostParam`
request from Hyperbridge (`evm/src/core/HostManager.sol`, then `EvmHost.updateHostParams`). The
```
