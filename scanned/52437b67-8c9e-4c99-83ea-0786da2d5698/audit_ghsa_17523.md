# [H] DNN.PLATFORM possibly allows bypass of IP Filters

## Summary
Severity: High
Advisory: GHSA-fjhg-3mrh-mm7h
CVE: CVE-2025-52487
CWE: CWE-863
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-fjhg-3mrh-mm7h
Type: github-advisory

## Affected
- NuGet: `DNN.PLATFORM` — affected >=7.0.0 <10.0.1

## Details
DNN.PLATFORM allows a specially crafted request or proxy to be created that would bypass the design of DNN Login IP Filters allowing login attempts from IP Adresses not in the allow list. This vulnerability is fixed in 10.0.1.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-fjhg-3mrh-mm7h
- https://nvd.nist.gov/vuln/detail/CVE-2025-52487
- https://github.com/dnnsoftware/Dnn.Platform
