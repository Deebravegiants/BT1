# [H] Server-Side Request Forgery in groupoffice

## Summary
Severity: High
Advisory: CVE-2023-46730
Aliases: GHSA-vw6c-h82w-mvfv
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-11-07
Source: https://osv.dev/vulnerability/CVE-2023-46730
Type: osv

## Details
Group-Office is an enterprise CRM and groupware tool. In affected versions there is full Server-Side Request Forgery (SSRF) vulnerability in the /api/upload.php endpoint. The /api/upload.php endpoint does not filter URLs which allows a malicious user to cause the server to make resource requests to untrusted domains. Note that protocols like file:// can also be used to access the server disk. The request result (on success) can then be retrieved using /api/download.php. This issue has been addressed in versions 6.8.15, 6.7.54, and 6.6.177. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46730.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-vw6c-h82w-mvfv
- https://nvd.nist.gov/vuln/detail/CVE-2023-46730
- https://github.com/Intermesh/groupoffice/commit/99205535e8cec6592fd7f1469837926f27c72d50
