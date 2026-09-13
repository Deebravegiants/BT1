# [M] CVE-2021-34981

## Summary
Severity: Medium
Advisory: CVE-2021-34981
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/CVE-2021-34981
Type: osv

## Details
Linux Kernel Bluetooth CMTP Module Double Free Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of Linux Kernel. An attacker must first obtain the ability to execute high-privileged code on the target system in order to exploit this vulnerability.

The specific flaw exists within the CMTP module. The issue results from the lack of validating the existence of an object prior to performing further free operations on the object. An attacker can leverage this vulnerability to escalate privileges and execute code in the context of the kernel. Was ZDI-CAN-11977.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-21-1223/
