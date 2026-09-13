# [H] BrowserStack Cypress CL: Command Injection via cypress_config_file leads to arbitrary code execution through malicious browserstack.json

## Summary
Severity: High
Advisory: CVE-2026-48723
Aliases: GHSA-fh4c-mffm-8xhf
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-48723
Type: osv

## Details
The browserstack-cypress-cli is BrowserStack's CLI which allows users to run Cypress tests on BrowserStack. Versions prior to 1.36.4 are vulnerable to OS command injection via the cypress_config_file configuration parameter. In readCypressConfigUtil.js, the loadJsFile() function constructs a shell command by interpolating the user-controlled cypress_config_filepath value into a template literal, then executes it via child_process.execSync(). Shell metacharacters in the config path (specifically " and ;) allow breaking out of the quoted argument and injecting arbitrary commands. This issue has been fixed in version 1.36.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48723.json
- https://github.com/browserstack/browserstack-cypress-cli/security/advisories/GHSA-fh4c-mffm-8xhf
- https://nvd.nist.gov/vuln/detail/CVE-2026-48723
- https://github.com/browserstack/browserstack-cypress-cli/commit/6dbf8f9374c0e25eac818fbcb95f5705ded71710
