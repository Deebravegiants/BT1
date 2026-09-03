# [M] RPC DOS via TraceTx

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-11-nibiru
Published: 2024-11-28
Source: https://github.com/code-423n4/2024-11-nibiru-findings/issues/35
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/grpc_query.go#L547
https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/grpc_query.go#L511


# Vulnerability details

The TraceTx method in x/evm/keeper/grpc_query.go implements a gRPC query interface that allows simulation and tracing of specific transactions based on provided configurations. This method enables users to perform detailed execution simulations for transactions in a block.

However, a DOS issue arises during the simulation of predecessor transactions.

---

### Proof of Concept

Within the TraceTx function, predecessor transactions are simulated first, followed by transaction tracing:

https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/grpc_query.go#L547

```go
result, _, err := k.TraceEthTxMsg(ctx, cfg, txConfig, msg, req.TraceConfig, false, tracerConfig)
if err != nil {
    // error will be returned with detailed status from traceTx
    return nil, err
}
```

During the simulation of predecessor transactions, an attacker can exploit the process by providing an excessively large number of transactions in the req.Predecessors parameter. This forces the chain to repeatedly compute transaction results, maliciously consuming resources and leading to a denial of service.

https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/grpc_query.go#L511

```go
for i, tx := range req.Predecessors {
    ethTx := tx.AsTransaction()
    msg, err := ethTx.AsMessage(signer, cfg.BaseFeeWei)
    if err != nil {
        continue
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-11-nibiru-findings/issues/35_
