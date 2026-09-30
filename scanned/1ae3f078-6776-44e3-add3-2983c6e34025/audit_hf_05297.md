# [M] Chainlink router configured twice

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23595
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In BridgeCCIP, there is a dedicated storage slot for the CCIP router address, `router`:

```solidity
contract BridgeCCIP is CCIPReceiver, Ownable {
    address public router;
    // ...
}
```

This value can be updated by the admin through `BridgeCCIP::setRouter`:

```solidity
function setRouter(address _router) external onlyAdmin {
    require(_router != address(0), "!router");
    router = _router;
    emit SetRouter(msg.sender, _router);
}
```

The router is then used in `BridgeCCIP::send` to send messages via CCIP:

```solidity
IRouterClient(router).ccipSend{ value: msg.value }(_dstChain, evm2AnyMessage);
```

However, the inherited `CCIPReceiver` contract already defines an immutable router address (`i_ccipRouter`), which is used to validate that incoming CCIP messages originate from the correct router.  

This introduces an inconsistency: if `BridgeCCIP.router` is changed, the contract will continue to send messages via the new router, but receive messages only from the original, immutable `i_ccipRouter`. This mismatch could break cross-chain communication or make message delivery non-functional.

## Recommendation
Since the router address in `CCIPReceiver` is immutable, any future change to the router would already require redeployment of the `BridgeCCIP` contract. Therefore, the router storage slot and the `setRouter` function in `BridgeCCIP` are redundant and potentially misleading. We recommend removing both and relying exclusively on the `i_ccipRouter` value inherited from `CCIPReceiver`.
