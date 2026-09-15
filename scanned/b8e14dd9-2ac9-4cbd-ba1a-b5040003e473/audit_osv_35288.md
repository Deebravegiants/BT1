# [M] CVE-2025-70342

## Summary
Severity: Medium
Advisory: CVE-2025-70342
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2025-70342
Type: osv

## Details
erase-install prior to v40.4 commit 2c31239 writes swiftDialog credential output to a hardcoded path /var/tmp/dialog.json. This allows an unauthenticated attacker to intercept admin credentials entered during reinstall/erase operations via creating a named pipe.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70342.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70342
- https://github.com/grahampugh/erase-install/commit/2c31239fb8519d87577514b3db9ddb0771232a21
- https://github.com/grahampugh/erase-install/pull/574
- https://github.com/malvector/CVE-2025-70342
