# [H] Suricata is Vulnerable to Detection Bypass via Crafted Multiple SYN Packets

## Summary
Severity: High
Advisory: CVE-2025-59147
Aliases: GHSA-v8hv-6v7x-4c2r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-59147
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Versions 7.0.11 and below, as well as 8.0.0, are vulnerable to detection bypass when crafted traffic sends multiple SYN packets with different sequence numbers within the same flow tuple, which can cause Suricata to fail to pick up the TCP session. In IDS mode this can lead to a detection and logging bypass. In IPS mode this will lead to the flow getting blocked. This issue is fixed in versions 7.0.12 and 8.0.1.

## References
- https://forum.suricata.io/t/suricata-8-0-1-and-7-0-12-released/6018
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59147.json
- https://github.com/OISF/suricata/security/advisories/GHSA-v8hv-6v7x-4c2r
- https://nvd.nist.gov/vuln/detail/CVE-2025-59147
- https://github.com/OISF/suricata/commit/be6315dba0d9101b11d16e9dacfe2822b3792f1b
- https://github.com/OISF/suricata/commit/e91b03c90385db15e21cf1a0e85b921bf92b039e
