# [M] Uninitialized memory access in Motoko incremental garbage collector

## Summary
Severity: Medium
Advisory: CVE-2024-11991
Aliases: GHSA-9rhg-3qf8-hrv3
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-11991
Type: osv

## Details
Motoko's incremental garbage collector is impacted by an uninitialized memory access bug, caused by incorrect use of write barriers in a few locations. This vulnerability could potentially allow unauthorized read or write access to a Canister's memory. However, exploiting this bug requires the Canister to enable the incremental garbage collector or enhanced orthogonal persistence, which are non-default features in Motoko.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11991.json
- https://github.com/dfinity/motoko/security/advisories/GHSA-9rhg-3qf8-hrv3
- https://nvd.nist.gov/vuln/detail/CVE-2024-11991
- https://github.com/dfinity/motoko/pull/4677
