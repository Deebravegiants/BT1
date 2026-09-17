# [M] ALPINE-CVE-2016-8605

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-8605
Ecosystem: Alpine:v3.4
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-8605
Type: osv

## Affected
- Alpine:v3.4: `guile` — affected >=0 <2.0.11-r3

## Details
The mkdir procedure of GNU Guile temporarily changed the process' umask to zero. During that time window, in a multithreaded application, other threads could end up creating files with insecure permissions. For example, mkdir without the optional mode argument would create directories as 0777. This is fixed in Guile 2.0.13. Prior versions are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-8605
