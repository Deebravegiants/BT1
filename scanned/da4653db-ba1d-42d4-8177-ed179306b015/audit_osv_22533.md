# [M] Missing brute force protection on cloud federation sharing in Nextcloud Server

## Summary
Severity: Medium
Advisory: CVE-2022-31118
Aliases: GHSA-2vwh-5v93-3vcq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2022-08-04
Source: https://osv.dev/vulnerability/CVE-2022-31118
Type: osv

## Details
Nextcloud server is an open source personal cloud solution. In affected versions an attacker could brute force to find if federated sharing is being used and potentially try to brute force access tokens for federated shares (`a-zA-Z0-9` ^ 15). It is recommended that the Nextcloud Server is upgraded to 22.2.9, 23.0.6 or 24.0.2. Users unable to upgrade may disable federated sharing via the Admin Sharing settings in `index.php/settings/admin/sharing`.

## References
- https://github.com/nextcloud/server/pull/32843/commits/6eb692da7fe73c899cb6a8d2aa045eddb1f14018
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31118.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-2vwh-5v93-3vcq
- https://nvd.nist.gov/vuln/detail/CVE-2022-31118
