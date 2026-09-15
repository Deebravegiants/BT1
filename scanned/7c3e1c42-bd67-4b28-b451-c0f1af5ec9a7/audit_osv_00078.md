# [H] ALPINE-CVE-2016-2147

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2147
Ecosystem: Alpine:v3.4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2147
Type: osv

## Affected
- Alpine:v3.4: `busybox` — affected >=0 <1.24.2-r0

## Details
Integer overflow in the DHCP client (udhcpc) in BusyBox before 1.25.0 allows remote attackers to cause a denial of service (crash) via a malformed RFC1035-encoded domain name, which triggers an out-of-bounds heap write.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2147
