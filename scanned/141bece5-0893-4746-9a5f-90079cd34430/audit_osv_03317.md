# [C] ALPINE-CVE-2025-49796

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-49796
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-49796
Type: osv

## Affected
- Alpine:v3.21: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.13.9-r0

## Details
A vulnerability was found in libxml2. Processing certain sch:name elements from the input XML file can trigger a memory corruption issue. This flaw allows an attacker to craft a malicious XML input file that can lead libxml to crash, resulting in a denial of service or other possible undefined behavior due to sensitive data being corrupted in memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-49796
