# [H] PJSIP: Stack overflow parsing SDP a=crypto attributes

## Summary
Severity: High
Advisory: CVE-2026-57162
Aliases: GHSA-m9g3-jcj8-qjfm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-57162
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to commit a1b707c, a stack buffer overflow exists in the SRTP/SDES media transport when processing a=crypto attributes during SDP offer/answer (sdes_encode_sdp() in transport_srtp_sdes.c). This affects applications with SRTP enabled (use_srtp optional or mandatory, using SDES keying). During media negotiation, the crypto attributes from the remote SDP are collected into a fixed-size array without bounding their number; a remote peer that includes an excessive number of a=crypto attributes in a single media description can write past the end of that array on the stack. This is reachable from an incoming SIP INVITE during offer/answer, before application-level authentication. Impact may range from unexpected application termination to control flow hijack/memory corruption. Applications that do not enable SRTP are not affected. This issue has been patched via commit a1b707c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57162.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-m9g3-jcj8-qjfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-57162
- https://github.com/pjsip/pjproject/commit/a1b707c0c9b0506faf2a8a438b60f11ffd6a6fd9
