# [H] ALPINE-CVE-2019-15681

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-15681
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15681
Type: osv

## Affected
- Alpine:v3.10: `libvncserver` — affected >=0 <0.9.11-r3
- Alpine:v3.11: `libvncserver` — affected >=0 <0.9.12-r1
- Alpine:v3.7: `libvncserver` — affected >=0 <0.9.11-r3
- Alpine:v3.8: `libvncserver` — affected >=0 <0.9.11-r3
- Alpine:v3.9: `libvncserver` — affected >=0 <0.9.11-r3

## Details
LibVNC commit before d01e1bb4246323ba6fcee3b82ef1faa9b1dac82a contains a memory leak (CWE-655) in VNC server code, which allow an attacker to read stack memory and can be abused for information disclosure. Combined with another vulnerability, it can be used to leak stack memory and bypass ASLR. This attack appear to be exploitable via network connectivity. These vulnerabilities have been fixed in commit d01e1bb4246323ba6fcee3b82ef1faa9b1dac82a.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15681
