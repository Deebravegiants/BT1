# [M] PJSIP: SIP Multipart CID URI Length Underflow

## Summary
Severity: Medium
Advisory: CVE-2026-41415
Aliases: GHSA-935m-fmf5-j4pm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41415
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. In 2.16 and earlier, there is an out-of-bounds read when parsing a malformed Content-ID URI in SIP multipart message body. Insufficient length validation can cause reads beyond the intended buffer bounds. This vulnerability is fixed in 2.17.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41415.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-935m-fmf5-j4pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-41415
- https://github.com/pjsip/pjproject/commit/4225a93c16661538005017883fbc8f1ea1d5f4b0
