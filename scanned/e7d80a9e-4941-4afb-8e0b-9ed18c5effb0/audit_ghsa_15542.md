# [H] ic-cdk has a memory leak when calling a canister method via `ic_cdk::call`

## Summary
Severity: High
Advisory: GHSA-rwq6-crjg-9cpw
CVE: CVE-2024-7884
CWE: CWE-401
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-05
Source: https://github.com/advisories/GHSA-rwq6-crjg-9cpw
Type: github-advisory

## Affected
- crates.io: `ic_cdk` — affected >=0.8.0 <0.8.2
- crates.io: `ic_cdk` — affected >=0.9.0 <0.9.3
- crates.io: `ic_cdk` — affected >=0.10.0 <0.10.1
- crates.io: `ic_cdk` — affected >=0.11.0 <0.11.6
- crates.io: `ic_cdk` — affected >=0.12.0 <0.12.2
- crates.io: `ic_cdk` — affected >=0.13.0 <0.13.5
- crates.io: `ic_cdk` — affected >=0.14.0 <0.14.1
- crates.io: `ic_cdk` — affected >=0.15.0 <0.15.1

## Details
When a canister method is called via `ic_cdk::call*`, a new Future `CallFuture` is created  and can be awaited by the caller to get the execution result. Internally, the state of the Future is tracked and stored in a struct called `CallFutureState`.  A bug in the polling implementation of the `CallFuture` allows multiple references to be held for this internal state and not all references were dropped before the `Future` is resolved. Since we have unaccounted references held, a copy of the internal state ended up being persisted in the canister's heap and thus causing a memory leak. 

### Impact
Canisters built in Rust with `ic_cdk` and `ic_cdk_timers` are affected. If these canisters call a canister method, use timers or heartbeat, they will likely leak a small amount of memory on every such operation. **In the worst case, this could lead to heap memory exhaustion triggered by an attacker.**

Motoko based canisters are not affected by the bug.

### Patches
The patch has been backported to all minor versions between `>= 0.8.0, <= 0.15.0`. The patched versions available are `0.8.2, 0.9.3, 0.10.1, 0.11.6, 0.12.2, 0.13.5, 0.14.1, 0.15.1` and their previous versions have been yanked. 

### Workarounds
There are no known workarounds at the moment. Developers are recommended to upgrade their canister as soon as possible to the latest available patched version of `ic_cdk` to avoid running out of Wasm heap memory. 

> [!NOTE]  
> Upgrading the canisters (without updating `ic_cdk`) also frees the leaked memory but it's only a temporary solution.

### References
- [dfinity/cdk-rs/pull/509](https://github.com/dfinity/cdk-rs/pull/509)
- [ic_cdk docs](https://docs.rs/ic-cdk/latest/ic_cdk/)
- [Internet Computer Specification](https://internetcomputer.org/docs/current/references/ic-interface-spec)

## References
- https://github.com/dfinity/cdk-rs/security/advisories/GHSA-rwq6-crjg-9cpw
- https://nvd.nist.gov/vuln/detail/CVE-2024-7884
- https://github.com/dfinity/cdk-rs/pull/509
- https://github.com/dfinity/cdk-rs/commit/bd17d57a7b8ca59665fea5fad6143ca02724d03b
- https://docs.rs/ic-cdk/latest/ic_cdk
- https://github.com/dfinity/cdk-rs
- https://internetcomputer.org/docs/current/references/ic-interface-spec
- https://rustsec.org/advisories/RUSTSEC-2024-0372.html
