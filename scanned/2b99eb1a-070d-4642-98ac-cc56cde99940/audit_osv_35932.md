# [H] Crypt::OpenSSL::PKCS12 versions before 1.98 for Perl allow a NULL pointer dereference in print_attribute via a zero length BMPSTRING attribute

## Summary
Severity: High
Advisory: CVE-2026-17510
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/CVE-2026-17510
Type: osv

## Details
Crypt::OpenSSL::PKCS12 versions before 1.98 for Perl allow a NULL pointer dereference in print_attribute via a zero length BMPSTRING attribute.

print_attribute() sizes the destination buffer for a BMPSTRING attribute from its declared byte length with `Renew(*attribute, length, char)`. A zero length attribute makes that a zero size reallocation, which Perl implements as a free returning NULL, so the buffer pointer becomes NULL, the following `strncpy` copies nothing, and the caller dereferences NULL in the `strlen()` it passes to `newSVpvn()`. A zero length BMPSTRING is even length, so the ASN.1 decoder accepts it and the value reaches this code. The UTF8STRING, OCTET STRING and BIT STRING arms size on `length + 1` or `length * 4 + 1` and are unaffected.

Any caller that passes an untrusted PKCS#12 file to info_as_hash() can crash the process. info() prints attribute values directly without sizing a buffer and is unaffected.

## References
- http://www.openwall.com/lists/oss-security/2026/08/09/1
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17510.json
- https://metacpan.org/release/JONASBN/Crypt-OpenSSL-PKCS12-1.98/source/Changes.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-17510
- https://github.com/dsully/perl-crypt-openssl-pkcs12/commit/6cb282d8d8e8ded4859551cd2d3cfa7c6028ce48.patch
- https://github.com/dsully/perl-crypt-openssl-pkcs12
