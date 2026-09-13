# [C] CVE-2017-15088

## Summary
Severity: Critical
Advisory: CVE-2017-15088
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-23
Source: https://osv.dev/vulnerability/CVE-2017-15088
Type: osv

## Details
plugins/preauth/pkinit/pkinit_crypto_openssl.c in MIT Kerberos 5 (aka krb5) through 1.15.2 mishandles Distinguished Name (DN) fields, which allows remote attackers to execute arbitrary code or cause a denial of service (buffer overflow and application crash) in situations involving untrusted X.509 data, related to the get_matching_data and X509_NAME_oneline_ex functions. NOTE: this has security relevance only in use cases outside of the MIT Kerberos distribution, e.g., the use of get_matching_data in KDC certauth plugin code that is specific to Red Hat.

## References
- http://www.securityfocus.com/bid/101594
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=871698
- https://bugzilla.redhat.com/show_bug.cgi?id=1504045
- https://github.com/krb5/krb5/commit/fbb687db1088ddd894d975996e5f6a4252b9a2b4
- https://github.com/krb5/krb5/pull/707
