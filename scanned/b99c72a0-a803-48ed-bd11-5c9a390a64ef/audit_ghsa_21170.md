# [H] Apache MXNet vulnerable to potential denial-of-service by excessive resource consumption

## Summary
Severity: High
Advisory: GHSA-xxj3-55p6-xg3h
CVE: CVE-2022-24294
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-25
Source: https://github.com/advisories/GHSA-xxj3-55p6-xg3h
Type: github-advisory

## Affected
- PyPI: `mxnet` — affected >=0 <1.9.1

## Details
A regular expression used in Apache MXNet (incubating) is vulnerable to a potential denial-of-service by excessive resource consumption. The bug could be exploited when loading a model in Apache MXNet that has a specially crafted operator name that would cause the regular expression evaluation to use excessive resources to attempt a match. This issue affects Apache MXNet versions prior to 1.9.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24294
- https://github.com/apache/mxnet
- https://github.com/apache/mxnet/releases/tag/1.9.1
- https://lists.apache.org/thread/b1fbfmvzlr2bbp95lqoh3mtovclfcl3o
- http://www.openwall.com/lists/oss-security/2022/07/24/2
