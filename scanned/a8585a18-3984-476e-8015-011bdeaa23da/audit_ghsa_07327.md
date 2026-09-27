# [M] serde_with: KeyValueMap serialization panics on empty sequence or map entries

## Summary
Severity: Medium
Advisory: GHSA-7gcf-g7xr-8hxj
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-7gcf-g7xr-8hxj
Type: github-advisory

## Affected
- crates.io: `serde_with` — affected >=2.3.0 <3.21.0

## Details
### Summary

The public `KeyValueMap` serializer assumes that each mapped element has at least one field or item to use as the map key, but it subtracts `1` from the caller-visible length before validating that assumption. An application that serializes attacker-controlled data through `#[serde_as(as = "KeyValueMap<_>")]` can be crashed by an empty inner sequence or map entry.

### Details

The affected public surface includes:

- Serialization of `#[serde_as(as = "KeyValueMap<_>")]` values through `serde_json::to_string` or any other Serde serializer`
- Public `KeyValueMap` conversions for sequence and map-backed entries`

The root cause is: The `KeyValueMap` serializer preallocating `Vec::with_capacity(len - 1)` or `Vec::with_capacity(len.unwrap_or(17) - 1)` before checking that the element actually contains the required first key field or item.

The vulnerable data/control flow is: attacker-controlled empty entry -> `serde_json::to_string` -> `KeyValueMap<TAs>::serialize_as` -> `SeqAsMapSerializer::{serialize_seq,serialize_map}` -> `Vec::with_capacity(len - 1)` or `Vec::with_capacity(len.unwrap_or(17) - 1)` -> panic

Relevant source locations:

- `serde_with/src/key_value_map.rs:590`
- `serde_with/src/key_value_map.rs:599`
- `serde_with/src/key_value_map.rs:613`
- `serde_with/src/key_value_map.rs:632`
- `serde_with/src/key_value_map.rs:648`

### PoC

```rust
/*
[dependencies]
serde = {version = "*", features = ["derive"]}
serde_with = "*"
serde_json = "*"
*/

use serde::Serialize;
use serde_with::{serde_as, KeyValueMap};

#[derive(Serialize)]
#[serde(transparent)]
struct Seq(Vec<String>);

#[serde_as]
#[derive(Serialize)]
#[serde(transparent)]
struct KVMap {
    #[serde_as(as = "KeyValueMap<_>")]
    foo: Vec<Seq>,
}

fn main() {
    let value = KVMap {
        foo: vec![Seq(Vec::new())],
    };
    let _ = serde_json::to_string(&value).unwrap();
}
```

### Impact

A local attacker who can trigger serialization of attacker-controlled data through `KeyValueMap` can terminate the process, causing a denial of service.

## References
- https://github.com/jonasbb/serde_with/security/advisories/GHSA-7gcf-g7xr-8hxj
- https://github.com/jonasbb/serde_with/pull/966
- https://github.com/jonasbb/serde_with/commit/c8a1d820ea25df01692b367058d587343e199389
- https://github.com/jonasbb/serde_with
- https://github.com/jonasbb/serde_with/compare/v2.2.0...v2.3.0
- https://github.com/jonasbb/serde_with/releases/tag/v3.21.0
