# [H] Libsolv: stack-based buffer overflow in libsolv eddsa pgp signature verification allows denial of service

## Summary
Severity: High
Advisory: CVE-2026-48863
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-48863
Type: osv

## Details
A flaw was found in libsolv. A stack-based buffer overflow vulnerability exists in the PGP verification component due to incorrect length handling when copying EdDSA 's' MPI into a stack buffer. A remote attacker could craft a malicious Ed25519 PGP signature with mismatched MPI lengths. Processing this crafted signature could lead to a denial of service in automated package or repository processing workflows.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48863.json
- https://access.redhat.com/security/cve/CVE-2026-48863
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48863.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48863
- https://bugzilla.redhat.com/show_bug.cgi?id=2460975
- https://github.com/openSUSE/libsolv/commit/44f8c085045b1f771641091bbb2b810d12cff9e8#diff-309f245ec9b669ec78b8159c39e6f50130b4d4a0448f742685f7833d04bc4caaR592
