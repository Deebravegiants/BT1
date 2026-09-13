# [M] CVE-2022-41317

## Summary
Severity: Medium
Advisory: CVE-2022-41317
Aliases: GHSA-rcg9-7fqm-83mq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/CVE-2022-41317
Type: osv

## Details
An issue was discovered in Squid 4.9 through 4.17 and 5.0.6 through 5.6. Due to inconsistent handling of internal URIs, there can be Exposure of Sensitive Information about clients using the proxy via an HTTPS request to an internal cache manager URL. This is fixed in 5.7.

## References
- http://www.squid-cache.org/Versions/v4/changesets/SQUID-2022_1.patch
- http://www.squid-cache.org/Versions/v5/changesets/SQUID-2022_1.patch
- https://www.openwall.com/lists/oss-security/2022/09/23/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41317.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-rcg9-7fqm-83mq
- https://nvd.nist.gov/vuln/detail/CVE-2022-41317
