# [H] CVE-2016-7444

## Summary
Severity: High
Advisory: CVE-2016-7444
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-09-27
Source: https://osv.dev/vulnerability/CVE-2016-7444
Type: osv

## Details
The gnutls_ocsp_resp_check_crt function in lib/x509/ocsp.c in GnuTLS before 3.4.15 and 3.5.x before 3.5.4 does not verify the serial length of an OCSP response, which might allow remote attackers to bypass an intended certificate validation mechanism via vectors involving trailing bytes left by gnutls_malloc.

## References
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00005.html
- http://www.securityfocus.com/bid/92893
- https://access.redhat.com/errata/RHSA-2017:2292
- https://lists.gnupg.org/pipermail/gnutls-devel/2016-September/008146.html
- https://www.gnutls.org/security.html
- https://gitlab.com/gnutls/gnutls/commit/964632f37dfdfb914ebc5e49db4fa29af35b1de9
