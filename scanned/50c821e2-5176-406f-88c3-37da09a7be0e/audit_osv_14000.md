# [C] CVE-2018-6334

## Summary
Severity: Critical
Advisory: CVE-2018-6334
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6334
Type: osv

## Details
Multipart-file uploads call variables to be improperly registered in the global scope. In cases where variables are not declared explicitly before being used this can lead to unexpected behavior. This affects all supported versions of HHVM prior to the patch (3.25.1, 3.24.5, and 3.21.9 and below).

## References
- https://github.com/facebook/hhvm/commit/6937de5544c3eead3466b75020d8382080ed0cff
- https://hhvm.com/blog/2018/03/30/hhvm-3.25.2.html
