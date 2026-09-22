# [H] Kimai (Authenticated) SSTI to RCE by Uploading a Malicious Twig File

## Summary
Severity: High
Advisory: CVE-2023-46245
Aliases: GHSA-fjhg-96cp-6fcw
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-31
Source: https://osv.dev/vulnerability/CVE-2023-46245
Type: osv

## Details
Kimai is a web-based multi-user time-tracking application. Versions prior to 2.1.0 are vulnerable to a Server-Side Template Injection (SSTI) which can be escalated to Remote Code Execution (RCE). The vulnerability arises when a malicious user uploads a specially crafted Twig file, exploiting the software's PDF and HTML rendering functionalities. Version 2.1.0 enables security measures for custom Twig templates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46245.json
- https://github.com/kimai/kimai/security/advisories/GHSA-fjhg-96cp-6fcw
- https://nvd.nist.gov/vuln/detail/CVE-2023-46245
- https://github.com/kimai/kimai/commit/38e37f1c2e91e1acb221ec5c13f11b735bd50ae4
