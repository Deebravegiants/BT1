# [M] ALPINE-CVE-2015-8631

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2015-8631
Ecosystem: Alpine:v3.4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8631
Type: osv

## Affected
- Alpine:v3.4: `krb5` — affected >=0 <1.14-r1

## Details
Multiple memory leaks in kadmin/server/server_stubs.c in kadmind in MIT Kerberos 5 (aka krb5) before 1.13.4 and 1.14.x before 1.14.1 allow remote authenticated users to cause a denial of service (memory consumption) via a request specifying a NULL principal name.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8631
