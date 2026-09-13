# [H] Open edX Platform: Insufficient Permission on set_course_mode_price()

## Summary
Severity: High
Advisory: CVE-2026-53635
Aliases: GHSA-rqq6-w4pv-7pjv
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-53635
Type: osv

## Details
Open edX Platform enables the authoring and delivery of online learning at any scale. Prior to commit 59bb6d6, the view function set_course_mode_price() at lms/djangoapps/instructor/views/instructor_dashboard.py:430 is decorated only with @login_required and performs no course-level permission check. Any authenticated user — including a learner account with zero course roles — can issue a single POST request to overwrite the honor mode price and currency of any course on the platform. The companion frontend modal was removed in a prior cleanup, but the URL route and view remain live, making this an unguarded orphan endpoint. This issue has been patched via commit 59bb6d6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53635.json
- https://github.com/openedx/openedx-platform/security/advisories/GHSA-rqq6-w4pv-7pjv
- https://nvd.nist.gov/vuln/detail/CVE-2026-53635
- https://github.com/openedx/openedx-platform/commit/59bb6d669e4fdc24d96afb809e12119372d9e257
- https://github.com/openedx/openedx-platform/commit/f25bbc4d52bd827c8f04c73de427e2e16a144c73
- https://github.com/openedx/openedx-platform/commit/fd93ef5f9940f4ad6f50cf7faecad8d9cf2d3336
