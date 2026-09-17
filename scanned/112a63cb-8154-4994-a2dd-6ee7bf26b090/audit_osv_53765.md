# [M] CVE-2023-23602

## Summary
Severity: Medium
Advisory: CVE-2023-23602
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-23602
Type: osv

## Details
A mishandled security check when creating a WebSocket in a WebWorker caused the Content Security Policy connect-src header to be ignored. This could lead to connections to restricted origins from inside WebWorkers. This vulnerability affects Firefox < 109, Firefox ESR < 102.7, and Thunderbird < 102.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-01/
- https://www.mozilla.org/security/advisories/mfsa2023-02/
- https://www.mozilla.org/security/advisories/mfsa2023-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1800890
