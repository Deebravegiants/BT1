# [H] GeoNode Server Side Request forgery

## Summary
Severity: High
Advisory: GHSA-rmxg-6qqf-x8mr
CVE: CVE-2023-40017
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-21
Source: https://github.com/advisories/GHSA-rmxg-6qqf-x8mr
Type: github-advisory

## Affected
- PyPI: `geonode` — affected >=3.2.0 <4.2.0

## Details
### Summary
A server side request forgery vuln was found within geonode when testing on a bug bounty program. Server side request forgery allows a user to request information on the internal service/services.

### Details
The endpoint /proxy/?url= does not properly protect against SSRF. when using the following format you can request internal hosts and display data. /proxy/?url=http://169.254.169.254\@whitelistedIPhere. This will state wether the AWS internal IP is alive. If you get a 404, the host is alive. A non alive host will not display a response. To display metadata, use a hashfrag on the url /proxy/?url=http://169.254.169.254\@#whitelisteddomain.com or try   /proxy/?url=http://169.254.169.254\@%23whitelisteddomain.com

### Impact
Port scan internal hosts, and request information from internal hosts.

## References
- https://github.com/GeoNode/geonode/security/advisories/GHSA-rmxg-6qqf-x8mr
- https://nvd.nist.gov/vuln/detail/CVE-2023-40017
- https://github.com/GeoNode/geonode/commit/a9eebae80cb362009660a1fd49e105e7cdb499b9
- https://github.com/GeoNode/geonode
- https://github.com/pypa/advisory-database/tree/main/vulns/geonode/PYSEC-2023-269.yaml
