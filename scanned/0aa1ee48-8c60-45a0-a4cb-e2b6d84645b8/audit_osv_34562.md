# [M] Icinga 2 Denial of Service (DoS) By Dereferencing Invalid Reference

## Summary
Severity: Medium
Advisory: CVE-2025-61908
Aliases: GHSA-v9jg-xqhj-f43g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-61908
Type: osv

## Details
Icinga 2 is an open source monitoring system. From 2.10.0 to before 2.15.1, 2.14.7, and 2.13.13, when creating an invalid reference, such as a reference to null, dereferencing results in a segmentation fault. This can be used by any API user with access to an API endpoint that allows specifying a filter expression to crash the Icinga 2 daemon. A fix is included in the following Icinga 2 versions: 2.15.1, 2.14.7, and 2.13.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61908.json
- https://github.com/Icinga/icinga2/security/advisories/GHSA-v9jg-xqhj-f43g
- https://nvd.nist.gov/vuln/detail/CVE-2025-61908
- https://github.com/Icinga/icinga2/pull/6521
- https://icinga.com/blog/releasing-icinga-2-v2-15-1-2-14-7-and-2-13-13-and-icinga-db-web-v1-2-3-and-1-1-4
