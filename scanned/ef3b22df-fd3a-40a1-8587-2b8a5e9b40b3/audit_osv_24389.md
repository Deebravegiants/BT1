# [H] local privilege escalation in apport-cli

## Summary
Severity: High
Advisory: CVE-2023-1326
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-04-13
Source: https://osv.dev/vulnerability/CVE-2023-1326
Type: osv

## Details
A privilege escalation attack was found in apport-cli 2.26.0 and earlier which is similar to CVE-2023-26604. If a system is specially configured to allow unprivileged users to run sudo apport-cli, less is configured as the pager, and the terminal size can be set: a local attacker can escalate privilege. It is extremely unlikely that a system administrator would configure sudo to allow unprivileged users to perform this class of exploit.

## References
- https://github.com/canonical/apport/
- https://github.com/canonical/apport/tags
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1326.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1326
- https://ubuntu.com/security/notices/USN-6018-1
- https://github.com/canonical/apport/commit/e5f78cc89f1f5888b6a56b785dddcb0364c48ecb
