# [C] CVE-2019-17006

## Summary
Severity: Critical
Advisory: CVE-2019-17006
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-22
Source: https://osv.dev/vulnerability/CVE-2019-17006
Type: osv

## Details
In Network Security Services (NSS) before 3.46, several cryptographic primitives had missing length checks. In cases where the application calling the library did not perform a sanity check on the inputs it could result in a crash due to a buffer overflow.

## References
- https://security.netapp.com/advisory/ntap-20210129-0001/
- https://us-cert.cisa.gov/ics/advisories/icsa-21-040-04
- https://cert-portal.siemens.com/productcert/pdf/ssa-379803.pdf
- https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS/NSS_3.46_release_notes
- https://bugzilla.mozilla.org/show_bug.cgi?id=1539788
