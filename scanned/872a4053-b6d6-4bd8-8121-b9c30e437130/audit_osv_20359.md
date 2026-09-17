# [C] CVE-2021-33191

## Summary
Severity: Critical
Advisory: CVE-2021-33191
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-24
Source: https://osv.dev/vulnerability/CVE-2021-33191
Type: osv

## Details
From Apache NiFi MiNiFi C++ version 0.5.0 the c2 protocol implements an "agent-update" command which was designed to patch the application binary. This "patching" command defaults to calling a trusted binary, but might be modified to an arbitrary value through a "c2-update" command. Said command is then executed using the same privileges as the application binary. This was addressed in version 0.10.0

## References
- https://lists.apache.org/thread.html/r6f27a2454f5f67dbe4e21c8eb1db537b01863a0bc3758f28aa60f032%40%3Cannounce.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/08/24/1
- https://www.openwall.com/lists/oss-security/2021/08/24/1
