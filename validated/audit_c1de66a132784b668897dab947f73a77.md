### Title
Lack of recovery mechanism for stuck native ETH in `HostManager` - (File: `evm/src/core/HostManager.sol`)

### Summary
`HostManager` implements a `receive() external payable {}` function that accepts arbitrary native ETH transfers, but the contract exposes no function — neither privileged nor governance-gated — to move that ETH back out. Its only outbound-value logic (`OnAcceptActions.Withdraw`) delegates to `IHostManager(_params.host).withdraw(withdrawParams)`, which withdraws revenue held by the `EvmHost`, not ETH held by `HostManager` itself. Any ETH sent directly to the `HostManager` address is therefore permanently unrecoverable. [1](#0-0) 

### Finding Description
`HostManager` is a governance-relay contract that receives cross-chain governance actions (`Withdraw`, `SetHostParam`, `SetAdmin`) from Hyperbridge via `onAccept`, and it deliberately accepts a native ETH `receive()` "for tests," with an explicit comment warning "Do not send any tokens directly to this contract." [2](#0-1) [1](#0-0) 

Despite this warning, the `receive()` function is `external payable` with no restriction, so any account — an unprivileged relayer, EOA, or contract — can send ETH to this address (accidentally or otherwise), e.g. via a plain transfer or as leftover `msg.value` from a mis-constructed call.

The contract's only value-moving code path is the `Withdraw` action inside `onAccept`, gated to require the caller be the bound `host` and the relayer be the `admin`: [3](#0-2) 

This branch calls `IHostManager(_params.host).withdraw(withdrawParams)` — i.e., it instructs the `EvmHost` contract to pay out revenue that the *host* holds (typically ERC-20 fee-token revenue), not ETH residing in the `HostManager` contract's own balance. There is no code path in `HostManager` that transfers out `address(this).balance`. Neither `SetHostParam` nor `SetAdmin` touch native balance either.

Consequently, once ETH lands in `HostManager`, no combination of `admin`, `host`, or Hyperbridge governance actions can retrieve it — the funds are permanently locked, exactly mirroring the reported bug class ("contract accepts ETH but has no `ethRescue`-equivalent function to recover it").

### Impact Explanation
Any ETH sent to the `HostManager` contract — whether via user error, a misconfigured integration that assumes it can pay native fees through the manager, or unspent `msg.value` from a batched call — is permanently and irrecoverably locked. This is a direct, permanent loss-of-funds condition matching the "Medium" severity classification of the original report: no privileged escalation is required to trigger the loss (only to send ETH, which is unprivileged), and no combination of on-chain governance calls can recover it.

### Likelihood Explanation
`HostManager` is deployed as a standard, publicly-addressable contract in the Hyperbridge EVM protocol stack, referenced by `EvmHost.hostParams().hostManager`. Because it exposes a permissionless `receive()` function, any transaction that sends value to this address (accidental transfers, integration bugs, or dust from failed multi-call flows) triggers the freeze. The likelihood of *some* ETH reaching this address over the contract's lifetime is non-trivial given it is a long-lived, address-known governance contract; the comment in the source ("Do not send any tokens directly to this contract") itself signals that the authors were aware this was already possible and risky, and chose to leave `receive()` open regardless (only annotated for test convenience).

### Recommendation
Add a governance-only (or `admin`-gated) rescue function to sweep native ETH out of `HostManager`, mirroring the pattern used elsewhere in the protocol for stray-balance recovery (e.g., `IntentGatewayV2`'s `SweepDust` action, which explicitly handles `token == address(0)` native transfers to a beneficiary):

```solidity
function rescueEth(address payable destination, uint256 amount) external restrict(msg.sender, _params.admin) {
    (bool sent, ) = destination.call{value: amount}("");
    require(sent, "HostManager: ETH transfer failed");
}
```

Alternatively, remove the permissionless `receive()` entirely if the contract is truly not meant to hold native ETH, so that stray transfers revert instead of becoming unrecoverable.

### Proof of Concept
1. Any account calls `hostManager.call{value: X}("")` (a plain ETH transfer) to a live `HostManager` deployment; `receive()` accepts it unconditionally. [1](#0-0) 
2. `address(hostManager).balance == X` from this point forward.
3. Even a legitimate Hyperbridge governance `Withdraw` request only reaches `onAccept`'s `Withdraw` branch, which calls `IHostManager(_params.host).withdraw(...)` — operating on the `EvmHost`'s balance, not `HostManager`'s own balance. [4](#0-3) 
4. No other `onAccept` action (`SetHostParam`, `SetAdmin`), nor any external function on `HostManager`, references `address(this).balance` or performs an outbound native transfer. [5](#0-4) 
5. `X` wei remains permanently locked in `HostManager` with no recovery path — confirming the freeze.

### Citations

**File:** evm/src/core/HostManager.sol (L44-52)
```text
contract HostManager is HyperApp, ERC165 {
    using Bytes for bytes;

    enum OnAcceptActions {
        Withdraw,
        SetHostParam,
        SetAdmin
    }

```

**File:** evm/src/core/HostManager.sol (L83-86)
```text
    /*
     * @dev fallback function for tests. Do not send any tokens directly to this contract.
     */
    receive() external payable {}
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
