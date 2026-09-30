# [H] Aubio is vulnerable to out of bound read when samplerate > 50kHz

## Summary
Severity: High
Advisory: GHSA-3x58-8qmv-wqw5
CVE: CVE-2018-14523
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3x58-8qmv-wqw5
Type: github-advisory

## Affected
- PyPI: `aubio` — affected >=0 <0.4.7

## Details
An issue was discovered in aubio 0.4.6. A buffer over-read can occur in `new_aubio_pitchyinfft` in `pitch/pitchyinfft.c` when the samplerate of the input file is larger than 50kHz.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14523
- https://github.com/aubio/aubio/issues/189
- https://github.com/aubio/aubio/commit/af4f9e6a93b629fb6defa2a229ec828885b9d187
- https://github.com/aubio/aubio
- https://github.com/pypa/advisory-database/tree/main/vulns/aubio/PYSEC-2018-63.yaml
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00071.html
