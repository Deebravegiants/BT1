# [H] CVE-2024-39934

## Summary
Severity: High
Advisory: CVE-2024-39934
CVSS: 7.8 (CVSS:3.1/AC:L/AV:L/A:H/C:H/I:H/PR:L/S:U/UI:N)
Published: 2024-07-04
Source: https://osv.dev/vulnerability/CVE-2024-39934
Type: osv

## Details
Robotmk before 2.0.1 allows a local user to escalate privileges (e.g., to SYSTEM) if automated Python environment setup is enabled, because the "shared holotree usage" feature allows any user to edit any Python environment.

## References
- https://checkmk.com/werk/16434
- https://github.com/elabit/robotmk/compare/v2.0.0...v2.0.1
- https://github.com/elabit/robotmk/releases/tag/v2.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39934.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39934
- https://github.com/elabit/robotmk/commit/78c1174ab2df43813050d0c22e1efb8636f8715e
