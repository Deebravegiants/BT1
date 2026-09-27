# [H] WinPmem Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: CVE-2024-10972
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:H)
Published: 2024-12-16
Source: https://osv.dev/vulnerability/CVE-2024-10972
Type: osv

## Details
Velocidex WinPmem versions 4.1 and below suffer from an Improper Input Validation vulnerability whereby an attacker with admin access can trigger a BSOD with a parallel thread changing the memory’s access right under the control of the user-mode application. This is due to verification only being performed at the beginning of the routine allowing the userspace to change page permissions half way through the routine.  A valid workaround is a rule to detect unauthorized loading of winpmem outside incident response operations.

## References
- https://github.com/Velocidex/WinPmem/releases/tag/v4.1.dev1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10972.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10972
