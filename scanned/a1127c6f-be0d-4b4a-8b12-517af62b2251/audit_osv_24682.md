# [H] CVE-2023-24832

## Summary
Severity: High
Advisory: CVE-2023-24832
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-24832
Type: osv

## Details
A null pointer dereference bug in Hermes prior to commit 5cae9f72975cf0e5a62b27fdd8b01f103e198708 could have been used by an attacker to crash an Hermes runtime where the EnableHermesInternal config option was set to true. Note that this is only exploitable in cases where Hermes is used to execute untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24832.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24832
- https://www.facebook.com/security/advisories/cve-2023-24832
- https://github.com/facebook/hermes/commit/5cae9f72975cf0e5a62b27fdd8b01f103e198708
