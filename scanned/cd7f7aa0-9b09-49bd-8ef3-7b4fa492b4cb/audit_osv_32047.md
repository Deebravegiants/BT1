# [C] Fedora Repository archive extraction path traversal

## Summary
Severity: Critical
Advisory: CVE-2025-23011
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2025-01-23
Source: https://osv.dev/vulnerability/CVE-2025-23011
Type: osv

## Details
Fedora Repository 3.8.1 allows path traversal when extracting uploaded archives ("Zip Slip"). A remote, authenticated attacker can upload a specially crafted archive that will extract an arbitrary JSP file to a location that can be executed by an unauthenticated GET request. Fedora Repository 3.8.1 was released on 2015-06-11 and is no longer maintained. Migrate to a currently supported version (6.5.1 as of 2025-01-23).

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-25-021-01.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23011.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23011
- https://github.com/fcrepo-exts/migration-utils
- https://github.com/fcrepo/fcrepo/releases
