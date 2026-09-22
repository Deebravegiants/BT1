# [H] CVE-2017-1000376

## Summary
Severity: High
Advisory: CVE-2017-1000376
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000376
Type: osv

## Details
libffi requests an executable stack allowing attackers to more easily trigger arbitrary code execution by overwriting the stack. Please note that libffi is used by a number of other libraries. It was previously stated that this affects libffi version 3.2.1 but this appears to be incorrect. libffi prior to version 3.1 on 32 bit x86 systems was vulnerable, and upstream is believed to have fixed this issue in version 3.1.

## References
- https://access.redhat.com/security/cve/CVE-2017-1000376
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
- http://www.debian.org/security/2017/dsa-3889
