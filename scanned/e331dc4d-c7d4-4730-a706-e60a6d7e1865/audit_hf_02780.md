# [H] Potential Fund Theft Due To Omni Network Downtime Or Paused OmniPortal

## Summary
Severity: High
Contest weight: 0.7664
Dataset id: 15178
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If an order is executed on the destination chain, the Solver sends a cross-rollup message via Omni Core to confirm that
the intent has been fulfilled on the inbox of the source chain. However, if the Omni network experiences downtime
or if the OmniPortal remains paused for more than 6 hours, this confirmation message will not be received on the
source chain within the expected timeframe. As a result, the order status remains Pending instead of being updated
to Filled.
```solidity
uint256 internal constant CLOSE_BUFFER = 6 hours;
_upsertOrder(id, Status.Filled, 0, creditedTo);
```
In this scenario, the order owner can call
close() on the source chain, even though their order has already been
fulfilled on the destination chain, allowing them to reclaim their deposited amount. This creates an opportunity for the
order owner to exploit the delay in the Omni network and effectively steal funds.
```solidity
function close(bytes32 id) external whenNotPaused(CLOSE) nonReentrant {
    OrderState memory state = _orderState[id];
    SolverNet.Header memory header = _orderHeader[id];
    if (state.status != Status.Pending) revert OrderNotPending();
    if (header.owner != msg.sender) revert Unauthorized();
    if (header.fillDeadline + CLOSE_BUFFER >= block.timestamp) revert OrderStillValid();
    _upsertOrder(id, Status.Closed, 0, msg.sender);
    _transferDeposit(id, header.owner);
    emit Closed(id);
}
```

## Recommendation
Relying on a fixed 6-hour buffer is insufficient to mitigate this issue. A better approach would be to check whether
OmniPortal is paused before allowing order closure or to integrate an oracle to verify the operational status of the
Omni network.
