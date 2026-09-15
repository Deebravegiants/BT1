# [M] OpenReception: Unauthenticated POST /api/log accepts arbitrary content with CRLF injection and no size or rate limits

## Summary
Severity: Medium
Advisory: CVE-2026-48083
Aliases: GHSA-fw48-38r5-7ffj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48083
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. Prior to version 1.0.2, the `/api/log` endpoint accepts unauthenticated POST requests, applies no schema validation to the message body, writes attacker-controlled content directly into the application's stdout log, interprets newline characters as real line breaks, and enforces no size or rate limits. Three independent abuse modes follow: log injection (forge log lines that look like legitimate system events), log volume DoS (saturate the logging pipeline at sustained 100+ requests per second of small messages), and oversized-payload submission (100 KB payloads accepted; larger sizes not tested). The most operationally damaging mode is log injection. An attacker can inject lines that an operator scanning logs would mistake for real system errors, mask their own activity behind fake noise, or pollute SIEM alerting rules with crafted false positives. A line such as `[error]: injected admin error` injected from an unauthenticated source is indistinguishable from the application's own error output once written to disk. Version 1.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48083.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-fw48-38r5-7ffj
- https://nvd.nist.gov/vuln/detail/CVE-2026-48083
- https://github.com/open-reception/appointment-booking-software/commit/36104d21ee0b6616f1c10273ec9970a27cb56b57
