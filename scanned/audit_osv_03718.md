# [H] ALPINE-CVE-2026-42946

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42946
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42946
Type: osv

## Affected
- Alpine:v3.21: `nginx` — affected >=0 <1.26.3-r1
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r1
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r1
- Alpine:v3.24: `nginx` — affected >=0 <1.30.1-r0

## Details
A vulnerability exists in the ngx_http_scgi_module and ngx_http_uwsgi_module modules that may result in excessive memory allocation or an over-read of data. When scgi_pass or uwsgi_pass is configured, an unauthenticated attacker with man-in-the-middle (MITM) ability to control responses from an upstream server may be able to read the memory of the NGINX worker process or restart it.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42946
