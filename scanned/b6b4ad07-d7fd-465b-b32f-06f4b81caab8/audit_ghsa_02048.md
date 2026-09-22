# [H] Catastrophic backtracking in URL authority parser when passed URL containing many @ characters

## Summary
Severity: High
Advisory: GHSA-q2q7-5pp4-w6pg
CVE: CVE-2021-33503
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-q2q7-5pp4-w6pg
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=1.25.4 <1.26.5

## Details
### Impact

When provided with a URL containing many `@` characters in the authority component the authority regular expression exhibits catastrophic backtracking causing a denial of service if a URL were passed as a parameter or redirected to via an HTTP redirect.


### Patches

The issue has been fixed in urllib3 v1.26.5.

### References

- [CVE-2021-33503](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-33503)
- [JVNVU#92413403 (English)](https://jvn.jp/en/vu/JVNVU92413403/)
- [JVNVU#92413403 (Japanese)](https://jvn.jp/vu/JVNVU92413403/)
- [urllib3 v1.26.5](https://github.com/urllib3/urllib3/releases/tag/1.26.5)

### For more information
If you have any questions or comments about this advisory:
* Ask in our [community Discord](https://discord.gg/urllib3)
* Email [sethmichaellarson@gmail.com](mailto:sethmichaellarson@gmail.com)

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-q2q7-5pp4-w6pg
- https://nvd.nist.gov/vuln/detail/CVE-2021-33503
- https://github.com/urllib3/urllib3/commit/2d4a3fee6de2fa45eb82169361918f759269b4ec
- https://github.com/urllib3/urllib3/commit/5b047b645f5f93900d5e2fc31230848c25eb1f5f#diff-52026d639119bf1e0364836b4e8a18bd9ed3c95c6ba39b26534a5057a65e35bbR65
- https://github.com/advisories/GHSA-q2q7-5pp4-w6pg
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2021-108.yaml
- https://github.com/urllib3/urllib3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6SCV7ZNAHS3E6PBFLJGENCDRDRWRZZ6W
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FMUGWEAUYGGHTPPXT6YBD53WYXQGVV73
- https://security.gentoo.org/glsa/202107-36
- https://www.oracle.com/security-alerts/cpuoct2021.html
