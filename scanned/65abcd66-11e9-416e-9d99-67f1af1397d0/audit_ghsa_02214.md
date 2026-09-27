# [H] Soundness issue in raw-cpuid

## Summary
Severity: High
Advisory: GHSA-hvqc-pc78-x9wh
CVE: CVE-2021-26306
CWE: CWE-198, CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hvqc-pc78-x9wh
Type: github-advisory

## Affected
- crates.io: `raw-cpuid` — affected >=0 <9.0.0

## Details
VendorInfo::as_string(), SoCVendorBrand::as_string(), and ExtendedFunctionInfo::processor_brand_string() construct byte slices using std::slice::from_raw_parts(), with data coming from #[repr(Rust)] structs. This is always undefined behavior.
This flaw has been fixed in v9.0.0, by making the relevant structs #[repr(C)].

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26306
- https://github.com/gz/rust-cpuid/issues/40
- https://github.com/RustSec/advisory-db/pull/614
- https://github.com/gz/rust-cpuid
- https://rustsec.org/advisories/RUSTSEC-2021-0013.html
