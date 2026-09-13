# [M] CVE-2020-6812

## Summary
Severity: Medium
Advisory: CVE-2020-6812
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-6812
Type: osv

## Details
The first time AirPods are connected to an iPhone, they become named after the user's name by default (e.g. Jane Doe's AirPods.) Websites with camera or microphone permission are able to enumerate device names, disclosing the user's name. To resolve this issue, Firefox added a special case that renames devices containing the substring 'AirPods' to simply 'AirPods'. This vulnerability affects Thunderbird < 68.6, Firefox < 74, Firefox < ESR68.6, and Firefox ESR < 68.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-10/
- https://usn.ubuntu.com/4328-1/
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-08/
- https://www.mozilla.org/security/advisories/mfsa2020-09/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1616661
