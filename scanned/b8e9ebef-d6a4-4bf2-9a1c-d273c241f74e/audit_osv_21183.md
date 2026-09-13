# [M] CVE-2021-41111

## Summary
Severity: Medium
Advisory: CVE-2021-41111
Aliases: GHSA-mfqj-f22m-gv8j
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-02-28
Source: https://osv.dev/vulnerability/CVE-2021-41111
Type: osv

## Details
Rundeck is an open source automation service with a web console, command line tools and a WebAPI. Prior to versions 3.4.5 and 3.3.15, an authenticated user with authorization to read webhooks in one project can craft a request to reveal Webhook definitions and tokens in another project. The user could use the revealed webhook tokens to trigger webhooks. Severity depends on trust level of authenticated users and whether any webhooks exist that trigger sensitive actions. There are patches for this vulnerability in versions 3.4.5 and 3.3.15. There are currently no known workarounds.

## References
- https://github.com/rundeck/rundeck/security/advisories/GHSA-mfqj-f22m-gv8j
- https://github.com/rundeck/rundeck/commit/a3bdc06a0731da902593732022a5b9d2b4facec5
