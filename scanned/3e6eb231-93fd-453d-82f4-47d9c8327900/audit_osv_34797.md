# [M] PJSIP is vulnerable to buffer overflow in Opus PLC

## Summary
Severity: Medium
Advisory: CVE-2025-65102
Aliases: GHSA-w5vr-39x7-h8g5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/CVE-2025-65102
Type: osv

## Details
PJSIP is a free and open source multimedia communication library. Prior to version 2.16, Opus PLC may zero-fill the input frame as long as the decoder ptime, while the input frame length, which is based on stream ptime, may be less than that. This issue affects PJSIP users who use the Opus audio codec in receiving direction. The vulnerability can lead to unexpected application termination due to a memory overwrite. This issue has been patched in version 2.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65102.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-w5vr-39x7-h8g5
- https://nvd.nist.gov/vuln/detail/CVE-2025-65102
- https://github.com/pjsip/pjproject/commit/6e9bd2e7d25bba26f852771b40693f45da14fa8f
