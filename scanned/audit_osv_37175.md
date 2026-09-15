# [M] PJSIP: Stack buffer overflow in Opus codec parser

## Summary
Severity: Medium
Advisory: CVE-2026-29068
Aliases: GHSA-pqww-jrxr-457f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-29068
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to version 2.17, there is a stack buffer overflow vulnerability when pjmedia-codec parses an RTP payload contain more frames than the caller-provided frames can hold. This issue has been patched in version 2.17.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29068.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-pqww-jrxr-457f
- https://nvd.nist.gov/vuln/detail/CVE-2026-29068
- https://github.com/pjsip/pjproject/commit/6c9024511bf5307ff72efde1f90c9a2a226d8967
