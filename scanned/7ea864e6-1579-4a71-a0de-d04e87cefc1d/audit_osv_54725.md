# [H] CVE-2024-29944

## Summary
Severity: High
Advisory: CVE-2024-29944
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-22
Source: https://osv.dev/vulnerability/CVE-2024-29944
Type: osv

## Details
An attacker was able to inject an event handler into a privileged object that would allow arbitrary JavaScript execution in the parent process. Note: This vulnerability affects Desktop Firefox only, it does not affect mobile versions of Firefox. This vulnerability affects Firefox < 124.0.1 and Firefox ESR < 115.9.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-15/
- https://www.mozilla.org/security/advisories/mfsa2024-16/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1886852
- http://www.openwall.com/lists/oss-security/2024/03/23/1
- https://lists.debian.org/debian-lts-announce/2024/03/msg00028.html
