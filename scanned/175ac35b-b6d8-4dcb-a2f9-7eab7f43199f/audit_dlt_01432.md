# [?] Merge bitcoin/bitcoin#34085: cluster mempool: exploit SFL properties in txgraph

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-01-06
Source: https://github.com/bitcoin/bitcoin/commit/c60f9cb66ee78ffb2cf8b9bedafddfc35a7df186
Type: security-commit

## Details
Merge bitcoin/bitcoin#34085: cluster mempool: exploit SFL properties in txgraph

1808b5aaf7c4910122fcd088e03d790189907438 clusterlin: remove unused FixLinearization (cleanup) (Pieter Wuille)
34a77138b7a6f65a31c6273f2770e943cc0b474b txgraph: permit non-topological clusters to defer fixing (optimization) (Pieter Wuille)
3380e0cbb59b2a893faabfa8f9aa18e582a11c2f txgraph: use PostLinearize less prior to linearizing (Pieter Wuille)
62dd88624a7fba14d2dac32d94fd101eb378d1e7 txgraph: drop NEEDS_SPLIT_ACCEPTABLE (simplification) (Pieter Wuille)
01ffcf464a4679136185e323b5b0328695a5bd1e clusterlin: support fixing linearizations (feature) (Pieter Wuille)

Pull request description:

  Part of #30289, follow-up to #32545.

  This gets rid of `FixLinearization()` by integrating the functionality into `Linearize()`, and makes txgraph exploit that (by delaying fixing of clusters until their first re-linearization). It also reduces (but does not eliminate) the number of calls to `PostLinearize`, as the SFL linearization effectively performs something very similar to postlinearization when loading in an existing linearization already.

ACKs for top commit:
  instagibbs:
    reACK 1808b5aaf7c4910122fcd088e03d790189907438
  marcofleon:
    code review ACK 1808b5aaf7c4910122fcd088e03d790189907438

Tree-SHA512: 81cd9549de2968f5126079cbb532e2cb052ea8157c9c9ce37fd39ad2294105d7c79ee8d946c3d8f7af5b2119299a232c448b42a33e1e43ccc778a5b52957e387
