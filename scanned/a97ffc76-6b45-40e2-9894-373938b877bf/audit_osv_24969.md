# [M] Nextcloud Desktop client does not verify received singed certificate in end-to-end encryption

## Summary
Severity: Medium
Advisory: CVE-2023-29000
Aliases: GHSA-h82x-98q3-7534
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2023-29000
Type: osv

## Details
The Nextcloud Desktop Client is a tool to synchronize files from Nextcloud Server. Starting with version 3.0.0 and prior to version 3.7.0, by trusting that the server will return a certificate that belongs to the keypair of the user, a malicious server could get the desktop client to encrypt files with a key known to the attacker. This issue is fixed in Nextcloud Desktop 3.7.0. No known workarounds are available.

## References
- https://hackerone.com/reports/1679267
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29000.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-h82x-98q3-7534
- https://nvd.nist.gov/vuln/detail/CVE-2023-29000
- https://github.com/nextcloud/desktop/pull/4949
