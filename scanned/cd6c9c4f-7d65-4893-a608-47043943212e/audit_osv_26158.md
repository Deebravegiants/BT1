# [H] External apps using tokens issued by administrators and moderators can call admin APIs

## Summary
Severity: High
Advisory: CVE-2023-52077
Aliases: GHSA-pjj7-7hcj-9cpc
CVSS: 8.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L)
Published: 2023-12-27
Source: https://osv.dev/vulnerability/CVE-2023-52077
Type: osv

## Details
Nexkey is a lightweight fork of Misskey v12 optimized for small to medium size servers. Prior to 12.23Q4.5, Nexkey allows external apps using tokens issued by administrators and moderators to call admin APIs.  This allows malicious third-party apps to perform operations such as updating server settings, as well as compromise object storage and email server credentials. This issue has been patched in 12.23Q4.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52077.json
- https://github.com/nexryai/nexkey/security/advisories/GHSA-pjj7-7hcj-9cpc
- https://nvd.nist.gov/vuln/detail/CVE-2023-52077
- https://github.com/mei23/misskey-v12/commit/78173e376f14fcc1987b02196f5538bf5b18225c
- https://github.com/misskey-dev/misskey/commit/5150053275594278e9eb23e72d98b16593c4c230
- https://github.com/nexryai/nexkey/commit/a4e4c9c47c5f84ec7ccd309bde59d4ae5d7e5a98
