# [?] fix: Panic in mirror when cannot start indexing. (#14445)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-10-15
Source: https://github.com/near/nearcore/commit/6e70e39ca7ef972024c4f8dd159e76512d878a66
Type: security-commit

## Details
fix: Panic in mirror when cannot start indexing. (#14445)

If in `index_target_loop` we fail to start near node before we send
anything on `clients_tx` channel, `clients_tx` will be dropped which
would `clients_rx` panic with `RecvError` waiting on channel here:
https://github.com/near/nearcore/blob/ac2a2439b15cefdabfbc1d3f2c2891a3cc416e38/tools/mirror/src/lib.rs#L2018

That's not very useful in case something goes wrong since no information
about the original panic would be available. Instead it's better to
panic when something goes wrong before we are able to send message over
`clients_tx`.
