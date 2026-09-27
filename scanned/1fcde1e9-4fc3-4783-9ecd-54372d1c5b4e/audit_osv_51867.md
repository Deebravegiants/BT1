# [C] CVE-2021-43527

## Summary
Severity: Critical
Advisory: CVE-2021-43527
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-43527
Type: osv

## Details
NSS (Network Security Services) versions prior to 3.73 or 3.68.1 ESR are vulnerable to a heap overflow when handling DER-encoded DSA or RSA-PSS signatures. Applications using NSS for handling signatures encoded within CMS, S/MIME, PKCS \#7, or PKCS \#12 are likely to be impacted. Applications using NSS for certificate validation or other TLS, X.509, OCSP or CRL functionality may be impacted, depending on how they configure NSS. *Note: This vulnerability does NOT impact Mozilla Firefox.* However, email clients and PDF viewers that use NSS for signature verification, such as Thunderbird, LibreOffice, Evolution and Evince are believed to be impacted. This vulnerability affects NSS < 3.73 and NSS < 3.68.1.

## References
- https://ftp.mozilla.org/pub/security/nss/releases/NSS_3_68_1_RTM/
- https://ftp.mozilla.org/pub/security/nss/releases/NSS_3_73_RTM/
- https://security.gentoo.org/glsa/202212-05
- https://security.netapp.com/advisory/ntap-20211229-0002/
- https://cert-portal.siemens.com/productcert/pdf/ssa-594438.pdf
- https://www.mozilla.org/security/advisories/mfsa2021-51/
- https://www.starwindsoftware.com/security/sw-20220802-0001/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1737470
- https://www.oracle.com/security-alerts/cpuapr2022.html
