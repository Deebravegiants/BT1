# [M] CVE-2019-11749

## Summary
Severity: Medium
Advisory: CVE-2019-11749
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-11749
Type: osv

## Details
A vulnerability exists in WebRTC where malicious web content can use probing techniques on the getUserMedia API using constraints to reveal device properties of cameras on the system without triggering a user prompt or notification. This allows for the potential fingerprinting of users. This vulnerability affects Firefox < 69 and Firefox ESR < 68.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00017.html
- https://www.mozilla.org/security/advisories/mfsa2019-25/
- https://www.mozilla.org/security/advisories/mfsa2019-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1565374
