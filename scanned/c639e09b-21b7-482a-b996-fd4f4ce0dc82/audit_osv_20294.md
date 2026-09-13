# [M] CVE-2021-32728

## Summary
Severity: Medium
Advisory: CVE-2021-32728
Aliases: GHSA-f5fr-5gcv-6cc5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-18
Source: https://osv.dev/vulnerability/CVE-2021-32728
Type: osv

## Details
The Nextcloud Desktop Client is a tool to synchronize files from Nextcloud Server with a computer. Clients using the Nextcloud end-to-end encryption feature download the public and private key via an API endpoint. In versions prior to 3.3.0, the Nextcloud Desktop client fails to check if a private key belongs to previously downloaded public certificate. If the Nextcloud instance serves a malicious public key, the data would be encrypted for this key and thus could be accessible to a malicious actor. This issue is fixed in Nextcloud Desktop Client version 3.3.0. There are no known workarounds aside from upgrading.

## References
- https://www.debian.org/security/2021/dsa-4974
- https://github.com/nextcloud/desktop/pull/3338
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-f5fr-5gcv-6cc5
- https://hackerone.com/reports/1189162
