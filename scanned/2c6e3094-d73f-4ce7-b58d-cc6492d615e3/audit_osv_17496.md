# [M] CVE-2020-15661

## Summary
Severity: Medium
Advisory: CVE-2020-15661
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-08-10
Source: https://osv.dev/vulnerability/CVE-2020-15661
Type: osv

## Details
A rogue webpage could override the injected WKUserScript used by the logins autofill, this exploit could result in leaking a password for the current domain. This vulnerability affects Firefox for iOS < 28.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-34/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1654131
