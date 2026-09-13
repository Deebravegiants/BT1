# [M] File system exposure in Metabase

## Summary
Severity: Medium
Advisory: CVE-2022-24853
Aliases: GHSA-5cfq-582c-c38m
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2022-24853
Type: osv

## Details
Metabase is an open source business intelligence and analytics application. Metabase has a proxy to load arbitrary URLs for JSON maps as part of our GeoJSON support. While we do validation to not return contents of arbitrary URLs, there is a case where a particularly crafted request could result in file access on windows, which allows enabling an `NTLM relay attack`, potentially allowing an attacker to receive the system password hash. If you use Windows and are on this version of Metabase, please upgrade immediately. The following patches (or greater versions) are available: 0.42.4 and 1.42.4, 0.41.7 and 1.41.7, 0.40.8 and 1.40.8.

## References
- https://secure77.de/metabase-ntlm-relay-attack/
- https://www.qomplx.com/qomplx-knowledge-ntlm-relay-attacks-explained/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24853.json
- https://github.com/metabase/metabase/security/advisories/GHSA-5cfq-582c-c38m
- https://nvd.nist.gov/vuln/detail/CVE-2022-24853
