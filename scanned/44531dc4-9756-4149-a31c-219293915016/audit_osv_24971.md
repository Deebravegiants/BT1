# [H] Order GLPI plugin vulnerable to remote code execution from authenticated user

## Summary
Severity: High
Advisory: CVE-2023-29006
Aliases: GHSA-xfx2-qx2r-3wwm
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-29006
Type: osv

## Details
The Order GLPI plugin allows users to manage order management within GLPI. Starting with version 1.8.0 and prior to versions 2.7.7 and 2.10.1, an authenticated user that has access to standard interface can craft an URL that can be used to execute a system command. Versions 2.7.7 and 2.10.1 contain a patch for this issue. As a workaround, delete the `ajax/dropdownContact.php` file from the plugin.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29006.json
- https://github.com/pluginsGLPI/order/security/advisories/GHSA-xfx2-qx2r-3wwm
- https://nvd.nist.gov/vuln/detail/CVE-2023-29006
- https://github.com/pluginsGLPI/order/commit/c78e64b95e54d5e47d9835984c93049f245b579e
