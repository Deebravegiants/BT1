# [H] Talishar: Critical Path Traversal in gameName Parameter

## Summary
Severity: High
Advisory: CVE-2026-28429
Aliases: GHSA-f386-xhcw-jrx8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28429
Type: osv

## Details
Talishar is a fan-made Flesh and Blood project. Prior to commit 6be3871, a Path Traversal vulnerability was identified in the gameName parameter. While the application's primary entry points implement input validation, the ParseGamestate.php component can be accessed directly as a standalone script. In this scenario, the absence of internal sanitization allows for directory traversal sequences (e.g., ../) to be processed, potentially leading to unauthorized file access. This issue has been patched in commit 6be3871.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28429.json
- https://github.com/Talishar/Talishar/commit/6be3871a14c192d1fb8146cdbc76f29f27c1cf48
- https://github.com/Talishar/Talishar/security/advisories/GHSA-f386-xhcw-jrx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-28429
