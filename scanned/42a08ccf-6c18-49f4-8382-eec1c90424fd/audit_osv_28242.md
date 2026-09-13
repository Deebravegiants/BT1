# [C] Cacti command injection in cmd_realtime.php

## Summary
Severity: Critical
Advisory: CVE-2024-29895
Aliases: GHSA-cr28-x256-xf5m
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-29895
Type: osv

## Details
Cacti provides an operational monitoring and fault management framework. A command injection vulnerability on the 1.3.x DEV branch allows any unauthenticated user to execute arbitrary command on the server when `register_argc_argv` option of PHP is `On`. In `cmd_realtime.php` line 119, the `$poller_id` used as part of the command execution is sourced from `$_SERVER['argv']`, which can be controlled by URL when `register_argc_argv` option of PHP is `On`. And this option is `On` by default in many environments such as the main PHP Docker image for PHP. Commit 53e8014d1f082034e0646edc6286cde3800c683d contains a patch for the issue, but this commit was reverted in commit 99633903cad0de5ace636249de16f77e57a3c8fc.

## References
- https://github.com/Cacti/cacti/blob/501712998589763d411a68d35e3cda98fd9cfd18/cmd_realtime.php#L119
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29895.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-cr28-x256-xf5m
- https://nvd.nist.gov/vuln/detail/CVE-2024-29895
- https://github.com/Cacti/cacti/commit/53e8014d1f082034e0646edc6286cde3800c683d
- https://github.com/Cacti/cacti/commit/99633903cad0de5ace636249de16f77e57a3c8fc
