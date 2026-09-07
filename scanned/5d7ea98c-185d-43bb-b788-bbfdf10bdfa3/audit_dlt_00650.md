# [?] Fix panic on lightest mode client when requesting a block with unknown hash. (#1631)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-08-30
Source: https://github.com/celo-org/celo-blockchain/commit/43ae19064484233315e4dace800d16c19915e377
Type: security-commit

## Details
Fix panic on lightest mode client when requesting a block with unknown hash. (#1631)

Previously, if you use `eth_getBlock` on a lightest mode client, and specify a hash that doesn't correspond to a block, the entire client would crash due to a panic in client_handler.go.  This PR fixes that panic, and makes getting a block by an unknown hash return "unknown block", which is the desired behavior and also what you get when you request a block by an unknown number (a number that is higher than the last block's number).

This requires modifying the `HeaderRequest` ODR request type to properly work when receiving a response with no headers.  This PR modifies it to accept such responses if the request was by hash, but not if it was by number.  This opens the door for a malicious LES server to fool a light client into thinking there is no block with this hash, when in fact there is.  However, it's simpler and seems preferable to the alternative of querying all one's peers in case some of them are malicious this way, and only returning "unknown block" after querying all of them.  It's also preferable to the current status quo of malicious nodes being able to crash a lightest mode client by returning an empty response.  Note, too, that requesting the header by hash is only done through the RPC API and is not a common use-pattern by light client users.
