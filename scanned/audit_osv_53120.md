# [M] CVE-2022-29913

## Summary
Severity: Medium
Advisory: CVE-2022-29913
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-29913
Type: osv

## Details
The parent process would not properly check whether the Speech Synthesis feature is enabled, when receiving instructions from a child process. This vulnerability affects Thunderbird < 91.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1764778
