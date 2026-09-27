# [H] CVE-2017-17439

## Summary
Severity: High
Advisory: CVE-2017-17439
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/CVE-2017-17439
Type: osv

## Details
In Heimdal through 7.4, remote unauthenticated attackers are able to crash the KDC by sending a crafted UDP packet containing empty data fields for client name or realm. The parser would unconditionally dereference NULL pointers in that case, leading to a segmentation fault. This is related to the _kdc_as_rep function in kdc/kerberos5.c and the der_length_visible_string function in lib/asn1/der_length.c.

## References
- http://www.h5l.org/pipermail/heimdal-announce/2017-December/000008.html
- http://h5l.org/advisories.html?show=2017-12-08
- http://www.h5l.org/pipermail/heimdal-discuss/2017-August/000259.html
- https://github.com/heimdal/heimdal/commit/1a6a6e462dc2ac6111f9e02c6852ddec4849b887
- https://www.debian.org/security/2017/dsa-4055
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=878144
- https://github.com/heimdal/heimdal/issues/353
