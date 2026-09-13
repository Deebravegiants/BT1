# [H] ALPINE-CVE-2016-7444

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7444
Ecosystem: Alpine:v3.2
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-09-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7444
Type: osv

## Affected
- Alpine:v3.2: `gnutls` — affected >=0 <3.4.5-r1

## Details
The gnutls_ocsp_resp_check_crt function in lib/x509/ocsp.c in GnuTLS before 3.4.15 and 3.5.x before 3.5.4 does not verify the serial length of an OCSP response, which might allow remote attackers to bypass an intended certificate validation mechanism via vectors involving trailing bytes left by gnutls_malloc.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7444
