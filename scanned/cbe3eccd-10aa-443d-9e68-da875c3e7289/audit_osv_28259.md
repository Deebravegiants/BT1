# [M] mailcow Path Traversal and Arbitrary Code Execution Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-30270
Aliases: GHSA-4m8r-87gc-3vvp
CVSS: 6.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-30270
Type: osv

## Details
mailcow: dockerized is an open source groupware/email suite based on docker. A security vulnerability has been identified in mailcow affecting versions prior to 2024-04. This vulnerability is a combination of path traversal and arbitrary code execution, specifically targeting the `rspamd_maps()` function. It allows authenticated admin users to overwrite any file writable by the www-data user by exploiting improper path validation. The exploit chain can lead to the execution of arbitrary commands on the server. Version 2024-04 contains a patch for the issue.

## References
- https://mailcow.email/posts/2024/release-2024-04
- https://www.vicarius.io/vsociety/posts/mailcow-with-xss-and-path-traversal-cve-2024-31204-and-cve-2024-30270
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30270.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-4m8r-87gc-3vvp
- https://nvd.nist.gov/vuln/detail/CVE-2024-30270
- https://www.sonarsource.com/blog/remote-code-execution-in-mailcow-always-sanitize-error-messages
