# [C] weixin-python XML External Entity vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h384-ph77-3699
CVE: CVE-2018-25082
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-21
Source: https://github.com/advisories/GHSA-h384-ph77-3699
Type: github-advisory

## Affected
- PyPI: `weixin-python` — affected >=0 <0.5.5

## Details
A vulnerability was found in zwczou WeChat SDK Python 0.3.0 and classified as critical. This issue affects the function validate/to_xml. The manipulation leads to xml external entity reference. The attack may be initiated remotely. Upgrading to version 0.5.5 is able to address this issue. The name of the patch is e54abadc777715b6dcb545c13214d1dea63df6c9. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-223403.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25082
- https://github.com/zwczou/weixin-python/pull/30
- https://github.com/zwczou/weixin-python/commit/e54abadc777715b6dcb545c13214d1dea63df6c9
- https://github.com/zwczou/weixin-python
- https://github.com/zwczou/weixin-python/releases/tag/v0.5.5
- https://vuldb.com/?ctiid.223403
- https://vuldb.com/?id.223403
