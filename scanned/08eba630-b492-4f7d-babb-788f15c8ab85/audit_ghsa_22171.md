# [H] Aubio is vulnerable to denial of service via aubio_source_avcodec_readframe function

## Summary
Severity: High
Advisory: GHSA-rcv6-7hmv-fj7h
CVE: CVE-2018-14521
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rcv6-7hmv-fj7h
Type: github-advisory

## Affected
- PyPI: `aubio` — affected >=0 <0.4.7

## Details
An issue was discovered in aubio 0.4.6. A SEGV signal can occur in `aubio_source_avcodec_readframe` in `io/source_avcodec.c`, as demonstrated by aubiomfcc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14521
- https://github.com/aubio/aubio/issues/187
- https://github.com/aubio/aubio/commit/a81b12a3b4174953b3bc7ef4c37103f4d5636740
- https://github.com/aubio/aubio
- https://github.com/pypa/advisory-database/tree/main/vulns/aubio/PYSEC-2018-61.yaml
