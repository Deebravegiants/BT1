# [H] Use After Free in lucet

## Summary
Severity: High
Advisory: GHSA-hf79-8hjp-rrvq
CVE: CVE-2021-43790
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-30
Source: https://github.com/advisories/GHSA-hf79-8hjp-rrvq
Type: github-advisory

## Affected
- crates.io: `lucet-runtime` — affected >=0

## Details
### Impact
There is a bug in the main branch of Lucet's `lucet-runtime` that allows a use-after-free in an `Instance` object that could result in memory corruption, data race, or other related issues.  This bug was introduced early in the development of Lucet and is present in all releases.  As a result of this bug, and dependent on the memory backing for the `Instance` objects, it is possible to trigger a use-after-free when the `Instance` is dropped.

### Patches
Users should upgrade to the `main` branch of the Lucet repository. Lucet does not provide versioned releases on crates.io.

### Workarounds
There is no way to remediate this vulnerability without upgrading.

### Description
Lucet uses a "pool" allocator for new WebAssembly instances that are created. This pool allocator manages everything from the linear memory of the wasm instance, the runtime stack for async switching, as well as the memory behind the Instance itself. `Instances` are referred to via an `InstanceHandle` type which will, on drop, release the memory backing the Instance back to the pool.

When an Instance is dropped, the fields of the `Instance` are destructed top-to-bottom, however when the `alloc: Alloc` field is destructed, the memory backing the `Instance` is released back to the pool before the destructors of the remaining fields are run. If another thread allocates the same memory from the pool while these destructors are still running, a race condition occurs that can lead to use-after-free errors.

The bug was corrected by changing how the `InstanceHandle` destructor operates to ensure that the memory backing an Instance is only returned to the pool once the `Instance` has been completely destroyed.

This security advisory has been assigned CVE-2021-43790.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [lucet repository](https://github.com/bytecodealliance/lucet)
* Email [the lucet team](mailto:lucet@fastly.com)
* See the [Bytecode Alliance security policy](https://bytecodealliance.org/security)

## References
- https://github.com/bytecodealliance/lucet/security/advisories/GHSA-hf79-8hjp-rrvq
- https://nvd.nist.gov/vuln/detail/CVE-2021-43790
- https://github.com/bytecodealliance/lucet/commit/7c7757c772fb709c61b1442bcc1e1fbee97bf4a8
- https://crates.io/crates/lucet-runtime
- https://github.com/bytecodealliance/lucet
- https://rustsec.org/advisories/RUSTSEC-2021-0155.html
