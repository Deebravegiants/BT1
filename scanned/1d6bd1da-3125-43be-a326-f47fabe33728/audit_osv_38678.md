# [C] PJSIP: Asymmetric ptime integer overflow in Media Stream

## Summary
Severity: Critical
Advisory: CVE-2026-41416
Aliases: GHSA-f33g-8hjq-62xr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41416
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. In 2.16 and earlier, there is an integer overflow in media stream buffer size calculation when processing SDP with asymmetric ptime configuration. The overflow may result in an undersized buffer allocation, which can lead to unexpected application termination or memory corruption This vulnerability is fixed in 2.17.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41416.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-f33g-8hjq-62xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41416
- https://github.com/pjsip/pjproject/commit/66fe416c96e957417621b7be16e9e587d159f9bb
