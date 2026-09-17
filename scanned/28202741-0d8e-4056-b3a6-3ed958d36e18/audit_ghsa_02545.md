# [H] Improper Synchronization and Race Condition in vm-memory

## Summary
Severity: High
Advisory: GHSA-mm4m-qg48-f7wc
CVE: CVE-2020-13759
CWE: CWE-362, CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mm4m-qg48-f7wc
Type: github-advisory

## Affected
- crates.io: `vm-memory` — affected >=0 <0.1.1
- crates.io: `vm-memory` — affected >=0.2.0 <0.2.1

## Details
rust-vmm vm-memory before 0.1.1 and 0.2.x before 0.2.1 allows attackers to cause a denial of service (loss of IP networking) because read_obj and write_obj do not properly access memory. This affects aarch64 (with musl or glibc) and x86_64 (with musl).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13759
- https://github.com/rust-vmm/vm-memory/issues/93
- https://github.com/rust-vmm/vm-memory
- https://github.com/rust-vmm/vm-memory/releases/tag/v0.1.1
- https://github.com/rust-vmm/vm-memory/releases/tag/v0.2.1
- https://rustsec.org/advisories/RUSTSEC-2020-0157.html
