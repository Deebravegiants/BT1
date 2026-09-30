# [M] Wazuh: Heap-based Buffer Overflow in syscheck Registry Wildcard Expansion (LPE / DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-40106
Aliases: GHSA-qvrc-pcfc-jhqc
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-40106
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. Versions 4.6.0 and above prior to 4.14.5 contain a heap-based buffer overflow vulnerability in the syscheck component of the Wazuh agent for Windows. When expanding registry paths containing wildcards (* or ?), the agent allocates a fixed-size heap buffer of 256 bytes (OS_SIZE_256). By creating a registry subkey with a maximum allowed length (255 characters) inside a monitored path, a low-privileged local attacker can force an out-of-bounds write during string concatenation. Since wazuh-agent.exe runs as NT AUTHORITY\SYSTEM, this can lead to a silent Denial of Service (blinding the agent) or potentially Local Privilege Escalation (LPE). This issue has been fixed in version 4.14.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40106.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-qvrc-pcfc-jhqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-40106
