# [M] Insight API transaction broadcast endpoint can result in Full Path Disclosure

## Summary
Severity: Medium
Advisory: GHSA-8p2p-p8mg-x3cw
CVE: CVE-2018-1000023
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-8p2p-p8mg-x3cw
Type: github-advisory

## Affected
- npm: `insight-api` — affected >=0

## Details
Bitpay/insight-api Insight-api version 5.0.0 and earlier contains a CWE-20: input validation vulnerability in transaction broadcast endpoint that can result in Full Path Disclosure. This attack appear to be exploitable via Web request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000023
- https://github.com/bitpay/insight-api/issues/542
- https://github.com/advisories/GHSA-8p2p-p8mg-x3cw
- https://github.com/bitpay/insight-api
