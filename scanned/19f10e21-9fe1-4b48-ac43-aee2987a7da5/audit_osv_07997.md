# [C] CVE-2016-1000004

## Summary
Severity: Critical
Advisory: CVE-2016-1000004
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-19
Source: https://osv.dev/vulnerability/CVE-2016-1000004
Type: osv

## Details
Insufficient type checks were employed prior to casting input data in SimpleXMLElement_exportNode and simplexml_import_dom. This issue affects HHVM versions prior to 3.9.5, all versions between 3.10.0 and 3.12.3 (inclusive), and all versions between 3.13.0 and 3.14.1 (inclusive).

## References
- https://www.facebook.com/security/advisories/cve-2016-1000004
- https://github.com/facebook/hhvm/commit/8e7266fef1f329b805b37f32c9ad0090215ab269
