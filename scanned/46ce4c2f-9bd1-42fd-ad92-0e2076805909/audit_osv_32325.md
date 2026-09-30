# [H] GStreamer Incorrect Permission Assignment Local Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-2759
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-2759
Type: osv

## Details
GStreamer Incorrect Permission Assignment Local Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of GStreamer. An attacker must first obtain the ability to execute low-privileged code on the target system in order to exploit this vulnerability.

The specific flaw exists within the product installer. The issue results from incorrect permissions on folders. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of a target user. Was ZDI-CAN-25448.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2759.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2759
- https://www.zerodayinitiative.com/advisories/ZDI-25-268/
