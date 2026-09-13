# [C] ALPINE-CVE-2026-4408

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-4408
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4408
Type: osv

## Affected
- Alpine:v3.23: `samba` — affected >=4.1.0 <4.22.10-r0
- Alpine:v3.24: `samba` — affected >=4.1.0 <4.23.8-r0

## Details
A flaw was found in Samba. A remote attacker can exploit a misconfiguration in Samba file servers and classic domain controllers that use the "check password script" feature. If this script is configured with the %u substitution character, the client-controlled username is passed without proper escaping of shell meta-characters. This vulnerability allows an attacker to achieve remote command execution on the affected system. This issue primarily affects non-standard configurations where the "check password script" is used with %u and the samba-dcerpcd service is started as a system service.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4408
