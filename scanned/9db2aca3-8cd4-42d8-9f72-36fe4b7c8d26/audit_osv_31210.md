# [H] Windscribe Directory Traversal Local Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-6141
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2024-6141
Type: osv

## Details
Windscribe Directory Traversal Local Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of Windscribe. An attacker must first obtain the ability to execute low-privileged code on the target system in order to exploit this vulnerability.

The specific flaw exists within the Windscribe Service. The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of SYSTEM. Was ZDI-CAN-23441.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6141.json
- https://github.com/Windscribe/Desktop-App/blob/90a5cc3c1f50f6545f83969c2ace6b4ac2c91c4e/client/common/changelog.txt#L23
- https://nvd.nist.gov/vuln/detail/CVE-2024-6141
- https://www.zerodayinitiative.com/advisories/ZDI-24-820/
