# [H] node-tar Vulnerable to Arbitrary File Creation/Overwrite via Hardlink Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-24842
Aliases: GHSA-34x7-hfp2-rc4v
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24842
Type: osv

## Details
node-tar,a Tar for Node.js, contains a vulnerability in versions prior to 7.5.7 where the security check for hardlink entries uses different path resolution semantics than the actual hardlink creation logic. This mismatch allows an attacker to craft a malicious TAR archive that bypasses path traversal protections and creates hardlinks to arbitrary files outside the extraction directory. Version 7.5.7 contains a fix for the issue.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24842.json
- https://access.redhat.com/errata/RHSA-2026:18480
- https://access.redhat.com/errata/RHSA-2026:18868
- https://access.redhat.com/errata/RHSA-2026:2900
- https://access.redhat.com/errata/RHSA-2026:33371
- https://access.redhat.com/errata/RHSA-2026:5447
- https://access.redhat.com/errata/RHSA-2026:6192
- https://access.redhat.com/security/cve/CVE-2026-24842
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24842.json
- https://github.com/isaacs/node-tar/security/advisories/GHSA-34x7-hfp2-rc4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-24842
- https://bugzilla.redhat.com/show_bug.cgi?id=2433645
- https://github.com/isaacs/node-tar/commit/f4a7aa9bc3d717c987fdf1480ff7a64e87ffdb46
