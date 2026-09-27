# [H] CVE-2019-19270

## Summary
Severity: High
Advisory: CVE-2019-19270
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-19270
Type: osv

## Details
An issue was discovered in tls_verify_crl in ProFTPD through 1.3.6b. Failure to check for the appropriate field of a CRL entry (checking twice for subject, rather than once for subject and once for issuer) prevents some valid CRLs from being taken into account, and can allow clients whose certificates have been revoked to proceed with a connection to the server.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OGBBCPLJSDPFG5EI5P5G7P4KEX7YSD5G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QR65XUHPCRU3NXTSFVF2J4GWRIHC7AHW/
- https://github.com/proftpd/proftpd/issues/859
