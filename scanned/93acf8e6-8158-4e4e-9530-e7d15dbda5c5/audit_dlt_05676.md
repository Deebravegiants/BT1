# [?] fix(rpc): eth_simulateV1 method handler crash (#1955)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2026-01-20
Source: https://github.com/0xPolygon/bor/commit/ec7192a693f25c13b5f71f5ef0af71cfb357e800
Type: security-commit

## Details
fix(rpc): eth_simulateV1 method handler crash (#1955)

* Verify BlobScheduleConfig before calling CalcBlobFee

* set Nil withdrawals for bor simulation

* simChainHeadReader implements core.BorStateSyncer

* simplify fork checking

* lint fixing

* Add non nil chainConfig for testcase

---------

Co-authored-by: Pratik Patil <pratikspatil024@gmail.com>
