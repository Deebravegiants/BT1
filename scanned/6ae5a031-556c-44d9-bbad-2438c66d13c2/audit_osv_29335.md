# [M] Two-Factor Authentication (2FA) Bypass in mailcow: dockerized

## Summary
Severity: Medium
Advisory: CVE-2024-41958
Aliases: GHSA-4fcc-q245-qqgg
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:L/A:N)
Published: 2024-08-05
Source: https://osv.dev/vulnerability/CVE-2024-41958
Type: osv

## Details
mailcow: dockerized is an open source groupware/email suite based on docker. A vulnerability has been discovered in the two-factor authentication (2FA) mechanism. This flaw allows an authenticated attacker to bypass the 2FA protection, enabling unauthorized access to other accounts that are otherwise secured with 2FA. To exploit this vulnerability, the attacker must first have access to an account within the system and possess the credentials of the target account that has 2FA enabled. By leveraging these credentials, the attacker can circumvent the 2FA process and gain access to the protected account. This issue has been addressed in the `2024-07` release. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41958.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-4fcc-q245-qqgg
- https://nvd.nist.gov/vuln/detail/CVE-2024-41958
- https://github.com/mailcow/mailcow-dockerized/commit/f33d82ffc11ed3438609d4e7a6baa78cb3305bc3
