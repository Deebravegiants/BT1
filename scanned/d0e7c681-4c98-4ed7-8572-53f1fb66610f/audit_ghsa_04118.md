# [C] splunk-sdk does not properly verify untrusted TLS server certificates

## Summary
Severity: Critical
Advisory: GHSA-f58w-649r-qjr9
CVE: CVE-2019-5729
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-03-25
Source: https://github.com/advisories/GHSA-f58w-649r-qjr9
Type: github-advisory

## Affected
- PyPI: `splunk-sdk` — affected >=0 <1.6.6

## Details
Splunk-SDK-Python before 1.6.6 does not properly verify untrusted TLS server certificates, which could result in man-in-the-middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5729
- https://github.com/advisories/GHSA-f58w-649r-qjr9
- https://github.com/pypa/advisory-database/tree/main/vulns/splunk-sdk/PYSEC-2019-203.yaml
- https://github.com/splunk/splunk-sdk-python
- https://www.splunk.com/view/SP-CAAAQAD
