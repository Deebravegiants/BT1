# [H] zstd vulnerable to buffer overrun

## Summary
Severity: High
Advisory: GHSA-5c9c-6x87-f9vm
CVE: CVE-2022-4899
CWE: CWE-400
Ecosystem: PyPI, SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-5c9c-6x87-f9vm
Type: github-advisory

## Affected
- SwiftURL: `github.com/facebook/zstd` — affected >=0 <1.5.4
- PyPI: `zstd` — affected >=0 <1.5.4.0

## Details
A vulnerability was found in zstd v1.4.10, where an attacker can supply an empty string as an argument to the command line tool to cause buffer overrun.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4899
- https://github.com/facebook/zstd/issues/3200
- https://github.com/facebook/zstd/pull/3220
- https://github.com/sergey-dryabzhinsky/python-zstd/commit/c8a619aebdbd6b838fbfef6e19325a70f631a4c6
- https://github.com/facebook/zstd
- https://github.com/pypa/advisory-database/tree/main/vulns/zstd/PYSEC-2023-121.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/C63HAGVLQA6FJNDCHR7CNZZL6VSLILB2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JEHRBBYYTPA4DETOM5XAKGCP37NUTLOA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QYLDK6ODVC4LJSDULLX6Q2YHTFOWABCN
- https://security.netapp.com/advisory/ntap-20230725-0005
