# [H] Kiwi TCMS has command injection vulnerability in changelog.yml CI workflow

## Summary
Severity: High
Advisory: CVE-2023-30628
Aliases: GHSA-cw6r-6ccx-5hwx, PYSEC-2023-273
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-30628
Type: osv

## Details
Kiwi TCMS is an open source test management system. In kiwitcms/Kiwi v12.2 and prior and kiwitcms/enterprise v12.2 and prior,
the `changelog.yml` workflow is vulnerable to command injection attacks because of using an untrusted `github.head_ref` field. The `github.head_ref` value is an attacker-controlled value. Assigning the value to `zzz";echo${IFS}"hello";#` can lead to command injection. Since the permission is not restricted, the attacker has a write-access to the repository. Commit 834c86dfd1b2492ccad7ebbfd6304bfec895fed2 of the kiwitcms/Kiwi repository and commit e39f7e156fdaf6fec09a15ea6f4e8fec8cdbf751 of the kiwitcms/enterprise repository contain a fix for this issue.

## References
- https://github.com/kiwitcms/Kiwi/blob/37bfb87696093ce0393160e2725949185cc0651d/.github/workflows/changelog.yml#L18
- https://securitylab.github.com/research/github-actions-untrusted-input/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30628.json
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-cw6r-6ccx-5hwx
- https://nvd.nist.gov/vuln/detail/CVE-2023-30628
- https://github.com/kiwitcms/Kiwi/commit/834c86dfd1b2492ccad7ebbfd6304bfec895fed2
- https://github.com/kiwitcms/enterprise/commit/e39f7e156fdaf6fec09a15ea6f4e8fec8cdbf751
