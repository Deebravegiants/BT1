### Title
`HyperbridgeLzEndpoint.setHost` leaves unsafe stale `feeToken` approval to the previous ISMP host - (File: `sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol`)

### Summary
`HyperbridgeLzEndpoint.send()` grants the current `_host` a `forceApprove` allowance equal to the endpoint's entire `feeToken` balance on every permissionless call, and `setHost()` can later repoint `_host` to a new ISMP host without ever revoking the allowance left on the old host address. This mirrors the reported Burner.sol pattern: rotating a trusted module reference leaves the superseded contract with an unrevoked, unlimited-in-practice ERC20 allowance it can later exploit.

### Finding Description
In `send()`, whenever a message is dispatched with `msg.value == 0` (i.e. paid with `feeToken`), the endpoint approves the *entire current balance* of `feeToken` to `_host`: [1](#0-0) 

This function is externally callable by anyone (`whenNotPaused`, no access control on the caller), so any unprivileged user routing an OFT/LZ message through this adapter triggers a fresh full-balance approval to whatever `_host` currently is.

Separately, `setHost()` — the only place `_host` is written — simply overwrites the stored host address and recomputes the default relayer fee; it performs no cleanup of the allowance previously granted to the outgoing host: [2](#0-1) 

Because `forceApprove` in `send()` sets the allowance to the balance held **at the time of that call**, and `setHost` never zeroes the old host's allowance, the outgoing host address retains an ERC20 `transferFrom` allowance up to whatever the endpoint's `feeToken` balance was at the last `send()` call before rotation. If more `feeToken` subsequently accumulates in the endpoint (e.g., from OFTs' `_payLzToken` transfers ahead of future `send()` calls, or simply because the balance at rotation time was itself substantial), the old host contract — which may be swapped out precisely because it is being deprecated, upgraded, or found to be buggy/compromised — can call `transferFrom` on `feeToken` to drain up to its lingering allowance from the endpoint's balance, exactly the abuse pattern described in the referenced Burner.sol report.

This is architecturally analogous to the reported bug class even though `setHost` is owner-gated: the vulnerability is not "a malicious owner," but that a *routine, necessary* host migration (the codebase's own host-rotation flow, e.g. `HostManager`/`updateHostParams`, shows host address rotation is an expected operational event) leaves a stale unlimited-style approval on the superseded contract, which can be abused if that old host is later found compromised or malicious.

### Impact Explanation
An old/compromised/malicious `_host` contract can call `feeToken.transferFrom(endpoint, attacker, allowance)` to steal `feeToken` funds held by `HyperbridgeLzEndpoint`, up to the stale allowance amount, even after the endpoint has migrated away from it. Since `feeToken` balances continuously flow through this contract as part of normal `send()` fee-token payments, this represents a concrete theft-of-funds vector reachable purely through the endpoint's normal operation plus a host rotation.

### Likelihood Explanation
Medium likelihood: host rotation is a normal, expected lifecycle event (the codebase's host-manager rotation flow demonstrates hosts/host params are expected to change over the protocol's life), and `send()` is called by any unprivileged relayer/OApp integrating with the endpoint, so the stale approval is set up automatically during ordinary usage — no attacker action is needed to create the condition, only a later compromise or malicious behavior of the retired host to exploit it.

### Recommendation
Before or when updating `_host` in `setHost`, revoke the allowance granted to the outgoing host:
```solidity
function setHost(address hostAddr, uint32 localEid) external onlyOwner {
    if (_host != address(0)) {
        address oldFeeToken = IDispatcher(_host).feeToken();
        IERC20(oldFeeToken).forceApprove(_host, 0);
    }
    _host = hostAddr;
    _eid = localEid;
    ...
}
```
Alternatively, avoid pre-approving the full balance in `send()` and instead approve only the exact `request.fee` amount needed per dispatch, minimizing any residual allowance exposure.

### Proof of Concept
1. Endpoint accumulates `feeToken` balance `B` from OFT fee payments.
2. Any user calls `send()` with `msg.value == 0`; this sets `feeToken.allowance(endpoint, hostA) = B` via `forceApprove`. [3](#0-2) 
3. Owner later calls `setHost(hostB, ...)` to migrate to a new host; `_host` becomes `hostB`, but `hostA`'s allowance `B` is never cleared. [4](#0-3) 
4. If `hostA` is later found compromised (or was replaced because it was buggy/malicious), it can call `feeToken.transferFrom(endpoint, hostA, B)` (or up to the endpoint's current `feeToken` balance, whichever is smaller) to steal funds, since the ERC20 allowance is still live.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L152-165)
```text
    /**
     * @notice Configures the ISMP host address and local endpoint ID
     * @param hostAddr The ISMP host contract address
     * @param localEid The LayerZero endpoint ID for this chain
     */
    function setHost(address hostAddr, uint32 localEid) external onlyOwner {
        _host = hostAddr;
        _eid = localEid;

        // Set default relayer fee to $0.30 based on feeToken decimals
        address feeToken = IDispatcher(hostAddr).feeToken();
        uint8 decimals = IERC20Metadata(feeToken).decimals();
        _defaultRelayerFee = (3 * 10 ** decimals) / 10; // 0.30
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L296-306)
```text
        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            // Fee tokens already transferred to this contract by OFT's _payLzToken.
            // The quoted lzTokenFee includes a buffer above the relayer fee so the
            // legacy deployed host's per-byte protocol fee can be paid out of it;
            // approve our full feeToken balance and let the host take what it needs.
            address feeToken = IDispatcher(_host).feeToken();
            IERC20(feeToken).forceApprove(_host, IERC20(feeToken).balanceOf(address(this)));
            IDispatcher(_host).dispatch(request);
        }
```
