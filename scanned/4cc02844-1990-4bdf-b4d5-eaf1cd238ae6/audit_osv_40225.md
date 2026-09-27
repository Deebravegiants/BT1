# [H] CVE-2026-5172

## Summary
Severity: High
Advisory: CVE-2026-5172
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-5172
Type: osv

## Details
A buffer overflow in dnsmasq’s extract_addresses() function allows an attacker to trigger a heap out-of-bounds read and crash by exploiting a malformed DNS response, enabling extract_name() to advance the pointer past the record’s end.

## References
- https://github.com/pi-hole/FTL/releases/tag/v6.6.2
- https://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2026q2/018471.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-5172.json
- https://thekelleys.org.uk/dnsmasq/CVE/
- https://www.kb.cert.org/vuls/id/471747
- https://access.redhat.com/errata/RHSA-2026:19158
- https://access.redhat.com/security/cve/CVE-2026-5172
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5172
- https://bugzilla.redhat.com/show_bug.cgi?id=2458521
- https://github.com/NixOS/nixpkgs/pull/519082
- https://github.com/NixOS/nixpkgs/pull/519093
