# [M] Nextcloud Server has improper restriction of excessive authentication attempts on WebDAV endpoint

## Summary
Severity: Medium
Advisory: CVE-2023-39960
Aliases: GHSA-2hrc-5fgp-c9c9
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2023-10-13
Source: https://osv.dev/vulnerability/CVE-2023-39960
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. In Nextcloud Server starting with 25.0.0 and prior to 25.09 and 26.04; as well as Nextcloud Enterprise Server starting with 22.0.0 and prior to 22.2.10.14, 23.0.12.9, 24.0.12.5, 25.0.9, and 26.0.4; missing protection allows an attacker to brute force passwords on the WebDAV API. Nextcloud Server 25.0.9 and 26.0.4 and Nextcloud Enterprise Server 22.2.10.14, 23.0.12.9, 24.0.12.5, 25.0.9, and 26.0.4 contain patches for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/1924212
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39960.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-2hrc-5fgp-c9c9
- https://nvd.nist.gov/vuln/detail/CVE-2023-39960
- https://github.com/nextcloud/server/pull/38046
