# [M] CVE-2020-15720

## Summary
Severity: Medium
Advisory: CVE-2020-15720
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2020-07-14
Source: https://osv.dev/vulnerability/CVE-2020-15720
Type: osv

## Details
In Dogtag PKI through 10.8.3, the pki.client.PKIConnection class did not enable python-requests certificate validation. Since the verify parameter was hard-coded in all request functions, it was not possible to override the setting. As a result, tools making use of this class, such as the pki-server command, may have been vulnerable to Person-in-the-Middle attacks in certain non-localhost use cases. This is fixed in 10.9.0-b1.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1855273
- https://github.com/dogtagpki/pki/commit/50c23ec146ee9abf28c9de87a5f7787d495f0b72
- https://github.com/dogtagpki/pki/compare/v10.9.0-a2...v10.9.0-b1
