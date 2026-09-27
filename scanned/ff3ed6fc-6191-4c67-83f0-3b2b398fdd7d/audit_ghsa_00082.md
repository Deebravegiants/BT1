# [H] Regular Expression Denial of Service in charset

## Summary
Severity: High
Advisory: GHSA-9cp3-fh5x-xfcj
CVE: CVE-2017-16098
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-08-09
Source: https://github.com/advisories/GHSA-9cp3-fh5x-xfcj
Type: github-advisory

## Affected
- npm: `charset` — affected >=0 <1.0.1

## Details
Affected versions of `charset` are susceptible to a regular expression denial of service.

The amplification on this vulnerability is relatively low - it takes around 2 seconds for the engine to execute on a malicious input which is 50,000 characters in length.


If node was compiled using the `-DHTTP_MAX_HEADER_SIZE` however, the impact of the vulnerability can be significant, as the primary limitation for the vulnerability is the default max HTTP header length in node.


## Recommendation

Update to version 1.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16098
- https://github.com/node-modules/charset/issues/10
- https://github.com/node-modules/charset/pull/11
- https://github.com/node-modules/charset/commit/effda0c48c51b47a47f4cad7db0c51ee7407cc1b
- https://github.com/node-modules/charset
