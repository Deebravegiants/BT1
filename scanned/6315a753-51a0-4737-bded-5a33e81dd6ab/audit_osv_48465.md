# [H] CVE-2017-7843

## Summary
Severity: High
Advisory: CVE-2017-7843
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7843
Type: osv

## Details
When Private Browsing mode is used, it is possible for a web worker to write persistent data to IndexedDB and fingerprint a user uniquely. IndexedDB should not be available in Private Browsing mode and this stored data will persist across multiple private browsing mode sessions because it is not cleared when exiting. This vulnerability affects Firefox ESR < 52.5.2 and Firefox < 57.0.1.

## References
- http://www.securityfocus.com/bid/102112
- https://access.redhat.com/errata/RHSA-2017:3382
- https://lists.debian.org/debian-lts-announce/2017/12/msg00003.html
- https://www.debian.org/security/2017/dsa-4062
- https://www.mozilla.org/security/advisories/mfsa2017-28/
- http://www.securitytracker.com/id/1039954
- https://www.mozilla.org/security/advisories/mfsa2017-27/
- http://www.securityfocus.com/bid/102039
- https://bugzilla.mozilla.org/show_bug.cgi?id=1410106
