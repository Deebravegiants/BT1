# [M] CVE-2018-6526

## Summary
Severity: Medium
Advisory: CVE-2018-6526
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6526
Type: osv

## Details
view_all_bug_page.php in MantisBT 2.10.0-development before 2018-02-02 allows remote attackers to discover the full path via an invalid filter parameter, related to a filter_ensure_valid_filter call in current_user_api.php.

## References
- http://www.securityfocus.com/bid/103065
- https://mantisbt.org/bugs/view.php?id=23921
- https://github.com/mantisbt/mantisbt/commit/de686a9e6d8c909485b87ca09c8f912bf83082f2
