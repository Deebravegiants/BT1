# [M] Fedora Repository fedoraIntCallUser default credentials

## Summary
Severity: Medium
Advisory: CVE-2025-23012
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2025-01-23
Source: https://osv.dev/vulnerability/CVE-2025-23012
Type: osv

## Details
Fedora Repository 3.8.x includes a service account (fedoraIntCallUser) with default credentials and privileges to read read local files by manipulating datastreams. Fedora Repository 3.8.1 was released on 2015-06-11 and is no longer maintained. Migrate to a currently supported version (6.5.1 as of 2025-01-23).

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-25-021-01.json
- https://wiki.lyrasis.org/display/FEDORA38/XACML+Policy+Enforcement#XACMLPolicyEnforcement-4.1fedora-usersattributes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23012.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23012
- https://github.com/fcrepo-exts/migration-utils
- https://github.com/fcrepo/fcrepo/releases
