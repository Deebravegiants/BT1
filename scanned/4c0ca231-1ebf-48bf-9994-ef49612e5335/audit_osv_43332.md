# [M] Unverified AXI Address in Subsystem Mode Commands Enables Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-7328
Aliases: GHSA-c5v4-q445-wv84
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:L/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-7328
Type: osv

## Details
Missing authorization in Caliptra Core Runtime Firmware (INVOKE_DPE_MLDSA87, CM_AES_GCM_DECRYPT_DMA, EXTERNAL_MAILBOX_CMD commands) in subsystem mode allows a privileged local attacker to cause a denial of service via mailbox commands containing unverified AXI addresses. The security impact beyond availability is integration-specific.

This issue affects Core Runtime Firmware: 2.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7328.json
- https://github.com/chipsalliance/caliptra-sw/security/advisories/GHSA-c5v4-q445-wv84
- https://nvd.nist.gov/vuln/detail/CVE-2026-7328
- https://github.com/chipsalliance/caliptra-sw
