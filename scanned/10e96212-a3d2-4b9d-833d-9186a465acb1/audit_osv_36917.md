# [C] PJSIP has a Heap-based Buffer Overflow vulnerability in its H.264 unpacketizer

## Summary
Severity: Critical
Advisory: CVE-2026-26967
Aliases: GHSA-x2hc-6969-g8v6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-26967
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. In versions 2.16 and below, there is a critical Heap-based Buffer Overflow vulnerability in PJSIP's H.264 unpacketizer. The bug occurs when processing malformed SRTP packets, where the unpacketizer reads a 2-byte NAL unit size field without validating that both bytes are within the payload buffer bounds. The vulnerability affects applications that receive video using H.264. A patch is available at https://github.com/pjsip/pjproject/commit/f821c214e52b11bae11e4cd3c7f0864538fb5491.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26967.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-x2hc-6969-g8v6
- https://nvd.nist.gov/vuln/detail/CVE-2026-26967
- https://github.com/pjsip/pjproject/commit/f821c214e52b11bae11e4cd3c7f0864538fb5491
