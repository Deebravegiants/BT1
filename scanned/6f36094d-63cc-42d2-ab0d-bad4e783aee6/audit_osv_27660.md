# [M] Security headers not set in vantage6-UI

## Summary
Severity: Medium
Advisory: CVE-2024-24562
Aliases: GHSA-gwq3-pvwq-4c9w
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2024-03-14
Source: https://osv.dev/vulnerability/CVE-2024-24562
Type: osv

## Details
vantage6-UI is the official user interface for the vantage6 server. In affected versions a number of security headers are not set. This issue has been addressed in commit `68dfa6614` which is expected to be included in future releases. Users are advised to upgrade when a new release is made. While an upgrade path is not available users may modify the docker image build to insert the headers into nginx.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24562.json
- https://github.com/vantage6/vantage6-UI/security/advisories/GHSA-gwq3-pvwq-4c9w
- https://nvd.nist.gov/vuln/detail/CVE-2024-24562
- https://github.com/vantage6/vantage6-UI/commit/68dfa661415182da0e5717bd58db3d00aedcbd2e
