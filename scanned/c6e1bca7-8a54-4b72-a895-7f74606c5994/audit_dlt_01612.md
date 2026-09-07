# [?] Fix potential underflow on `PrunerWatermark.wait_for` (#22171)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-05-22
Source: https://github.com/MystenLabs/sui/commit/3406f7c92cc0316a61b0502bf84c99fa8cf23285
Type: security-commit

## Details
Fix potential underflow on `PrunerWatermark.wait_for` (#22171)

## Description 

Previously:
wait_for was an i64 field on PrunerWatermark (since PrunerWatermark
represented the "stored" datatype)
The fn wait_for on PrunerWatermark checked self.wait_for > 0 then
Duration::from_millis, which works since self.wait_for is still an i64,
and thus can represent negative values

https://github.com/MystenLabs/sui/pull/21537/files#diff-e91aff7d4e8968395eb4a363dc2f6b5affae2cd76042e5ec1029661c80c1522b

Currently:
fn pruner_watermark of the Connection trait has the same query
"CAST({BigInt} + 1000 * EXTRACT(EPOCH FROM pruner_timestamp - NOW()) AS
BIGINT)", but now we immediately set it as a field on PrunerWatermark -
as u64, so that causes the underflow, turning potentially negative
numbers into a massive positive one
Later, the check self.wait_for_ms > 0 will return true, and pruner waits
an impossible amount of time

`2025-05-19T21:07:58.187014Z DEBUG
sui_indexer_alt_framework::pipeline::concurrent::pruner: Waiting to
prune pipeline="obj_info" wait_for=18446744073452109.806s`

```
postgres=> select pipeline, pruner_hi, pruner_timestamp, reader_lo, cast(120000 + 1000 * extract(epoch from pruner_timestamp - now()) as bigint)  from watermarks where pipeline = 'obj_info';
 pipeline | pruner_hi |      pruner_timestamp      | reader_lo |    int8     
----------+-----------+----------------------------+-----------+-------------
 obj_info |  70000000 | 2025-04-21 17:58:41.447523 | 132449987 | -2430754117
```

The pruner_timestamp is in the past, so we end up in this scenario.

The fix is to switch wait_for on PrunerWatermark to be i64 instead. Also
add tests for this case.


_Trimmed to 38 lines — full report: https://github.com/MystenLabs/sui/commit/3406f7c92cc0316a61b0502bf84c99fa8cf23285_
