# [C] ClipBucket V5 5.5.1 through 5.5.3-#153 OS Command Injection via Installer php_cli_filepath Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-80138
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80138
Type: osv

## Details
ClipBucket V5's web installer fails to properly validate or escape the php_cli_filepath parameter before passing it to shell execution. Unauthenticated attackers can submit a crafted POST request to the installer with a malicious php_cli_filepath value to execute arbitrary commands as the web server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80138.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80138
- https://www.vulncheck.com/advisories/clipbucket-v5-5.5.1-through-5.5.3-153-os-command-injection-via-installer-php-cli-filepath-parameter
- https://github.com/MacWarrior/clipbucket-v5/commit/36e7c6cfd81f62a091d2aeef96a8fc2fc2d85dc4
- https://github.com/MacWarrior/clipbucket-v5
- https://github.com/MacWarrior/clipbucket-v5/blob/5.5.3-%23153/upload/cb_install/functions_install.php
- https://github.com/MacWarrior/clipbucket-v5/blob/5.5.3-%23153/upload/includes/classes/system.class.php
