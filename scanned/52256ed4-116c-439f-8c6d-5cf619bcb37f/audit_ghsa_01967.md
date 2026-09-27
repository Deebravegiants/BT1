# [H] Exposure of sensitive information to an unauthorized actor in HyperKitty

## Summary
Severity: High
Advisory: GHSA-h39g-q63v-4h9p
CVE: CVE-2021-33038
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-h39g-q63v-4h9p
Type: github-advisory

## Affected
- PyPI: `HyperKitty` — affected >=0 <1.3.5

## Details
An issue was discovered in management/commands/hyperkitty_import.py in HyperKitty prior to 1.3.5. When importing a private mailing list's archives, these archives are publicly visible for the duration of the import. For example, sensitive information might be available on the web for an hour during a large migration from Mailman 2 to Mailman 3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33038
- https://github.com/advisories/GHSA-h39g-q63v-4h9p
- https://github.com/pypa/advisory-database/tree/main/vulns/hyperkitty/PYSEC-2021-77.yaml
- https://gitlab.com/mailman/hyperkitty
- https://gitlab.com/mailman/hyperkitty/-/blob/master/doc/news.rst#L83-L87
- https://gitlab.com/mailman/hyperkitty/-/commit/9025324597d60b2dff740e49b70b15589d6804fa
- https://gitlab.com/mailman/hyperkitty/-/issues/380
- https://techblog.wikimedia.org/2021/06/11/discovering-and-fixing-cve-2021-33038-in-mailman3
- https://www.debian.org/security/2021/dsa-4922
