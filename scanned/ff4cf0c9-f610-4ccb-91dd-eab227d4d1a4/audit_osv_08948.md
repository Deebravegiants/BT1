# [H] CVE-2016-7053

## Summary
Severity: High
Advisory: CVE-2016-7053
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/CVE-2016-7053
Type: osv

## Details
In OpenSSL 1.1.0 before 1.1.0c, applications parsing invalid CMS structures can crash with a NULL pointer dereference. This is caused by a bug in the handling of the ASN.1 CHOICE type in OpenSSL 1.1.0 which can result in a NULL value being passed to the structure callback if an attempt is made to free certain invalid encodings. Only CHOICE structures using a callback which do not handle NULL value are affected.

## References
- http://www.securitytracker.com/id/1037261
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03744en_us
- http://www.securityfocus.com/bid/94244
- https://www.openssl.org/news/secadv/20161110.txt
