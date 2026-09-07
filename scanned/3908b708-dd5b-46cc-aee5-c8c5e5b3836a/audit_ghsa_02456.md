# [M] Error on unsupported architectures in raw-cpuid

## Summary
Severity: Medium
Advisory: GHSA-jrf8-cmgg-gv2m
CVE: CVE-2021-26307
CWE: CWE-400, CWE-657
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jrf8-cmgg-gv2m
Type: github-advisory

## Affected
- crates.io: `raw-cpuid` — affected >=0 <9.0.0

## Details
native_cpuid::cpuid_count() exposes the unsafe __cpuid_count() intrinsic from core::arch::x86 or core::arch::x86_64 as a safe function, and uses it internally, without checking the safety requirement:

* The CPU the program is currently running on supports the function being called.

CPUID is available in most, but not all, x86/x86_64 environments. The crate compiles only on these architectures, so others are unaffected. This issue is mitigated by the fact that affected programs are expected to crash deterministically every time.

The flaw has been fixed in v9.0.0, by intentionally breaking compilation when targeting SGX or 32-bit x86 without SSE. This covers all affected CPUs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26307
- https://github.com/gz/rust-cpuid/issues/40
- https://github.com/gz/rust-cpuid/issues/41
- https://github.com/RustSec/advisory-db/pull/614
- https://github.com/gz/rust-cpuid/commit/91b676eecd01f2163e2984215e2c0ac89e30ce75
- https://github.com/gz/rust-cpuid
- https://rustsec.org/advisories/RUSTSEC-2021-0013.html
