# [H] ALPINE-CVE-2017-18190

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-18190
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-02-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-18190
Type: osv

## Affected
- Alpine:v3.5: `cups` — affected >=0 <2.2.2-r0

## Details
A localhost.localdomain whitelist entry in valid_host() in scheduler/client.c in CUPS before 2.2.2 allows remote attackers to execute arbitrary IPP commands by sending POST requests to the CUPS daemon in conjunction with DNS rebinding. The localhost.localdomain name is often resolved via a DNS server (neither the OS nor the web browser is responsible for ensuring that localhost.localdomain is 127.0.0.1).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-18190
