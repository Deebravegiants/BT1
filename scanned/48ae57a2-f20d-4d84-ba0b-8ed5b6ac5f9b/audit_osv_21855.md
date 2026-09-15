# [M] Auth bypass in Dark SDK

## Summary
Severity: Medium
Advisory: CVE-2022-0451
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2022-0451
Type: osv

## Details
Dart SDK contains the HTTPClient in dart:io library whcih includes authorization headers when handling cross origin redirects. These headers may be explicitly set and contain sensitive information. By default, HttpClient handles redirection logic. If a request is sent to example.com with authorization header and it redirects to an attackers site, they might not expect attacker site to receive authorization header. We recommend updating the Dart SDK to version 2.16.0 or beyond.

## References
- https://dart-review.googlesource.com/c/sdk/+/229947
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0451.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0451
- https://github.com/dart-lang/sdk/commit/57db739be0ad4629079bfa94840064f615d35abc
