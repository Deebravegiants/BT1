# [M] User without download rights can download older version of that file in nextcloud server

## Summary
Severity: Medium
Advisory: CVE-2023-28844
Aliases: GHSA-w47p-f66h-h2vj
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-03-31
Source: https://osv.dev/vulnerability/CVE-2023-28844
Type: osv

## Details
Nextcloud server is an open source home cloud implementation. In affected versions users that should not be able to download a file can still download an older version and use that for uncontrolled distribution. This issue has been addressed in versions 24.0.10 and 25.0.4. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28844.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-w47p-f66h-h2vj
- https://nvd.nist.gov/vuln/detail/CVE-2023-28844
- https://github.com/nextcloud/server/pull/36113
