# [M] CVE-2019-9793

## Summary
Severity: Medium
Advisory: CVE-2019-9793
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2019-9793
Type: osv

## Details
A mechanism was discovered that removes some bounds checking for string, array, or typed array accesses if Spectre mitigations have been disabled. This vulnerability could allow an attacker to create an arbitrary value in compiled JavaScript, for which the range analysis will infer a fully controlled, incorrect range in circumstances where users have explicitly disabled Spectre mitigations. *Note: Spectre mitigations are currently enabled for all users by default settings.*. This vulnerability affects Thunderbird < 60.6, Firefox ESR < 60.6, and Firefox < 66.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-11/
- https://access.redhat.com/errata/RHSA-2019:0966
- https://access.redhat.com/errata/RHSA-2019:1144
- https://www.mozilla.org/security/advisories/mfsa2019-07/
- https://www.mozilla.org/security/advisories/mfsa2019-08/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1528829
