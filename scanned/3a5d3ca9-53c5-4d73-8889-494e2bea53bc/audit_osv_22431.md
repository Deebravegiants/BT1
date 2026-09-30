# [M] Improper input-size validation on the user new session name in Nextcloud Server

## Summary
Severity: Medium
Advisory: CVE-2022-29243
Aliases: GHSA-7cwm-qph5-4h5w
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-05-31
Source: https://osv.dev/vulnerability/CVE-2022-29243
Type: osv

## Details
Nextcloud Server is the file server software for Nextcloud, a self-hosted productivity platform. Prior to versions 22.2.7 and 23.0.4, missing input-size validation of new session names allows users to create app passwords with long names. These long names are then loaded into memory on usage, resulting in impacted performance. Versions 22.2.7 and 23.0.4 contain a fix for this issue. There are currently no known workarounds available.

## References
- https://hackerone.com/reports/1153138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29243.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-7cwm-qph5-4h5w
- https://nvd.nist.gov/vuln/detail/CVE-2022-29243
- https://security.gentoo.org/glsa/202208-17
- https://github.com/nextcloud/server/pull/31658
