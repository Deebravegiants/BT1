# [H] $_internalConvertBucketIndexStats may crash the mongod server when working on no timeseries input

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9748
Aliases: CVE-2026-9748
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9748
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
The $_internalConvertBucketIndexStats stage used PauseExecution as a way to signal "skip this document" when an index stats conversion failed. But PauseExecution is not a general purpose skip mechanism, but rather a TeeBuffer-internal signal used solely by $facet to coordinate its sub-pipelines. When this stage is placed before $facet in a pipeline, TeeBuffer receives the unexpected PauseExecution from upstream and hits a hard invariant assertion, crashing mongod.

## References
- https://jira.mongodb.org/browse/SERVER-123951
- https://nvd.nist.gov/vuln/detail/CVE-2026-9748
