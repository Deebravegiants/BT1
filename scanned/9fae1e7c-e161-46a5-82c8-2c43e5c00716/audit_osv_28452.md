# [H] Misskey allows the impersonation and takeover of remote accounts with unnormalized signed activities

## Summary
Severity: High
Advisory: CVE-2024-32983
Aliases: GHSA-2vxv-pv3m-3wvj
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2024-06-03
Source: https://osv.dev/vulnerability/CVE-2024-32983
Type: osv

## Details
Misskey is an open source, decentralized microblogging platform. Misskey doesn't perform proper normalization on the JSON structures of incoming signed ActivityPub activity objects before processing them, allowing threat actors to spoof the contents of signed activities and impersonate the authors of the original activities. This vulnerability is fixed in 2024.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32983.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-2vxv-pv3m-3wvj
- https://nvd.nist.gov/vuln/detail/CVE-2024-32983
- https://github.com/misskey-dev/misskey/commit/d2a5bb39e344fcb84a24ae60faafe4694b227b88
