# [H] Misskey allows users to bypass authentication of Bull dashboard

## Summary
Severity: High
Advisory: CVE-2023-43793
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-43793
Type: osv

## Details
Misskey is an open source, decentralized social media platform. Prior to version 2023.9.0, by editing the URL, a user can bypass the authentication of the Bull dashboard, which is the job queue management UI, and access it. Version 2023.9.0 contains a fix. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43793.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-9fj2-gjcf-cqqc
- https://github.com/nexryai/nexkey/security/advisories/GHSA-g8w5-568f-ffwf
- https://nvd.nist.gov/vuln/detail/CVE-2023-43793
- https://github.com/misskey-dev/misskey/commit/c9aeccb2ab260ceedc126e6e366da8cd13ece4b2
