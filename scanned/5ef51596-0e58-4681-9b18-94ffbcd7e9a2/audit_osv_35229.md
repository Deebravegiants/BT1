# [M] CVE-2025-69644

## Summary
Severity: Medium
Advisory: CVE-2025-69644
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2025-69644
Type: osv

## Details
An issue was discovered in Binutils before 2.46. The objdump contains a denial-of-service vulnerability when processing a crafted binary with malformed debug information. A logic flaw in the handling of DWARF location list headers can cause objdump to enter an unbounded loop and produce endless output until manually interrupted. This issue affects versions prior to the upstream fix and allows a local attacker to cause excessive resource consumption by supplying a malicious input file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=455446bbdc8675f34808187de2bbad4682016ff7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69644.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69644
- https://sourceware.org/bugzilla/show_bug.cgi?id=33639
