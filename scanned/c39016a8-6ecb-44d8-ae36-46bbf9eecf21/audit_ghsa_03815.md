# [H] postfix-mta-sts-resolver Algorithm Downgrade vulnerability

## Summary
Severity: High
Advisory: GHSA-h92m-42h4-82f6
CVE: CVE-2019-16791
CWE: CWE-757
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-h92m-42h4-82f6
Type: github-advisory

## Affected
- PyPI: `postfix-mta-sts-resolver` — affected >=0 <0.5.1

## Details
## Incorrect query parsing

### Impact
All users of versions prior to 0.5.1 can receive incorrect response from daemon under rare conditions, rendering downgrade of effective STS policy.

### Patches
Problem has been patched in version 0.5.1

### Workarounds
Users may remediate this vulnerability without upgrading by applying [these patches](https://gist.github.com/Snawoot/b9da85d6b26dea5460673b29df1adc6b) to older suppoorted versions.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [postfix-mta-sts-resolver repo](https://github.com/Snawoot/postfix-mta-sts-resolver)
* Email me at [vladislav at vm-0 dot com](mailto:vladislav-ex-gh-advisory@vm-0.com)

## References
- https://github.com/Snawoot/postfix-mta-sts-resolver/security/advisories/GHSA-h92m-42h4-82f6
- https://nvd.nist.gov/vuln/detail/CVE-2019-16791
- https://gist.github.com/Snawoot/b9da85d6b26dea5460673b29df1adc6b
- https://github.com/Snawoot/postfix-mta-sts-resolver
- https://github.com/pypa/advisory-database/tree/main/vulns/postfix-mta-sts-resolver/PYSEC-2020-174.yaml
