# [M] Werkzeug possible resource exhaustion when parsing file data in forms

## Summary
Severity: Medium
Advisory: GHSA-q34m-jh98-gwm2
CVE: CVE-2024-49767
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-25
Source: https://github.com/advisories/GHSA-q34m-jh98-gwm2
Type: github-advisory

## Affected
- PyPI: `Werkzeug` — affected >=2.0.0rc1 <3.0.6
- PyPI: `Quart` — affected >=0 <0.20.0

## Details
Applications using Werkzeug to parse `multipart/form-data` requests are vulnerable to resource exhaustion. A specially crafted form body can bypass the `Request.max_form_memory_size` setting.


The `Request.max_content_length` setting, as well as resource limits provided by deployment software and platforms, are also available to limit the resources used during a request. This vulnerability does not affect those settings. All three types of limits should be considered and set appropriately when deploying an application.

## References
- https://github.com/pallets/werkzeug/security/advisories/GHSA-q34m-jh98-gwm2
- https://nvd.nist.gov/vuln/detail/CVE-2024-49767
- https://github.com/pallets/quart/commit/5e78c4169b8eb66b91ead3e62d44721b9e1644ee
- https://github.com/pallets/quart/commit/abb04a512496206de279225340ed022852fbf51f
- https://github.com/pallets/werkzeug/commit/50cfeebcb0727e18cc52ffbeb125f4a66551179b
- https://github.com/pallets/werkzeug/commit/cbb446fdcada7685fce936ded01b76c08dbd6eb5
- https://github.com/pallets/werkzeug
- https://github.com/pallets/werkzeug/releases/tag/3.0.6
- https://security.netapp.com/advisory/ntap-20250103-0007
