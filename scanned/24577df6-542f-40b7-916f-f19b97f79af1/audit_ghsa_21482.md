# [H] ckb type_id script resume may randomly fail

## Summary
Severity: High
Advisory: GHSA-mcmr-49x3-4jqm
Ecosystem: crates.io
Published: 2022-11-02
Source: https://github.com/advisories/GHSA-mcmr-49x3-4jqm
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0.100.0 <0.102.0

## Details
### Impact
https://github.com/nervosnetwork/ckb/blob/v0.101.2/script/src/verify.rs#L871-L879
TypeIdSystemScript resume handle is not correct when max_cycles is not enough, `ScriptError::ExceededMaximumCycles` will be raised directly ranther than suspend as expect, and also because script_group execution order is random, so this will happen randomly.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-mcmr-49x3-4jqm
- https://github.com/nervosnetwork/ckb
- https://github.com/nervosnetwork/ckb/blob/v0.101.2/script/src/verify.rs#L871-L879
