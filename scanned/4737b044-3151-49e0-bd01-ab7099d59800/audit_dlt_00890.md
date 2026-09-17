# [?] txverifier: fix out of bounds panic for logs with no topics (#4360)

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2025-04-24
Source: https://github.com/wormhole-foundation/wormhole/commit/8cb392c2feb75528ce55f0ec4c45a5c96e3df92a
Type: security-commit

## Details
txverifier: fix out of bounds panic for logs with no topics (#4360)

* txverifier: fix out of bounds panic for logs with no topics

- Adds handling for logs with no topics, fixing a panic in the code.
- Adds a unit test that passes a valid receipt with a log with no topics
  to ensure the code does not panic

An in-the-wild example of this occurring is the transaction
0xa3692c2469b2ac9e7010aa07e550a26f3f35a959e8c20b23fb0abc03d81e54b4

* update comment

* Update node/pkg/txverifier/evm.go
