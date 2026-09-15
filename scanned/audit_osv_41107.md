# [H] Apache CXF: No default restriction on the amount of form parameters per message

## Summary
Severity: High
Advisory: CVE-2026-57819
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-57819
Type: osv

## Details
Apache CXF allows to set a limit on the number of form parameters in a JAX-RS message via the "maxFormParameterCount" configuration option. However, no default limit is set which may lead to denial of service attacks when processing  requests with very large numbers of form parameters. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue by using a default limit of 500 parameters.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/15
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57819.json
- https://lists.apache.org/thread/2n14mk01bjc3lrsyhzrkwy8h86289mov
- https://nvd.nist.gov/vuln/detail/CVE-2026-57819
