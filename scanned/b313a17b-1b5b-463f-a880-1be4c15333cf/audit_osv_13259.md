# [C] CVE-2018-18928

## Summary
Severity: Critical
Advisory: CVE-2018-18928
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-04
Source: https://osv.dev/vulnerability/CVE-2018-18928
Type: osv

## Details
International Components for Unicode (ICU) for C/C++ 63.1 has an integer overflow in number::impl::DecimalQuantity::toScientificString() in i18n/number_decimalquantity.cpp.

## References
- https://bugs.chromium.org/p/chromium/issues/detail?id=900059
- https://unicode-org.atlassian.net/browse/ICU-20246
- https://github.com/unicode-org/icu/commit/53d8c8f3d181d87a6aa925b449b51c4a2c922a51
