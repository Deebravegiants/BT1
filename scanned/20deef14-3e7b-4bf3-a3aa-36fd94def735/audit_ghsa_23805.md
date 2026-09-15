# [H] TDQM Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-r7q7-xcjw-qx8q
CVE: CVE-2016-10075
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r7q7-xcjw-qx8q
Type: github-advisory

## Affected
- PyPI: `tqdm` — affected >=4.4.1 <4.11.2
- PyPI: `tqdm` — affected >=4.10.0 <4.11.2

## Details
The `tqdm._version` module in tqdm versions 4.4.1 and 4.10 allows local users to execute arbitrary code via a crafted repo with a malicious git log in the current working directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10075
- https://github.com/tqdm/tqdm/issues/328
- https://github.com/tqdm/tqdm/pull/330
- https://github.com/pypa/advisory-database/tree/main/vulns/tqdm/PYSEC-2017-74.yaml
- https://github.com/tqdm/tqdm
- https://security.gentoo.org/glsa/201807-01
- https://web.archive.org/web/20170214023533/http://www.securityfocus.com/bid/95143
- http://www.openwall.com/lists/oss-security/2016/12/28/8
