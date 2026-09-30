# [C] CVE-2016-1000030

## Summary
Severity: Critical
Advisory: CVE-2016-1000030
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2016-1000030
Type: osv

## Details
Pidgin version <2.11.0 contains a vulnerability in X.509 Certificates imports specifically due to improper check of return values from gnutls_x509_crt_init() and gnutls_x509_crt_import() that can result in code execution. This attack appear to be exploitable via custom X.509 certificate from another client. This vulnerability appears to have been fixed in 2.11.0.

## References
- https://access.redhat.com/security/cve/cve-2016-1000030
- https://pidgin.im/news/security/?id=91
- https://security.gentoo.org/glsa/201701-38
- https://www.suse.com/pt-br/security/cve/CVE-2016-1000030/
- https://bitbucket.org/pidgin/main/commits/d6fc1ce76ffe
