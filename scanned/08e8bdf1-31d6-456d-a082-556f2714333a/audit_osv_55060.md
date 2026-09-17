# [M] CVE-2025-0237

## Summary
Severity: Medium
Advisory: CVE-2025-0237
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-0237
Type: osv

## Details
The WebChannel API, which is used to transport various information across processes, did not check the sending principal but rather accepted the principal being sent. This could have led to privilege escalation attacks. This vulnerability affects Firefox < 134, Firefox ESR < 128.6, Thunderbird < 134, and Thunderbird < 128.6.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00004.html
- https://www.mozilla.org/security/advisories/mfsa2025-01/
- https://www.mozilla.org/security/advisories/mfsa2025-02/
- https://www.mozilla.org/security/advisories/mfsa2025-04/
- https://www.mozilla.org/security/advisories/mfsa2025-05/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1915257
