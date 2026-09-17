# [M] Open edX Platform: Stored CSS Injection in Email Notifications via Incomplete HTML Sanitization

## Summary
Severity: Medium
Advisory: CVE-2026-42857
Aliases: GHSA-4xv3-5j4x-q8g4
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42857
Type: osv

## Details
Open edX Platform enables the authoring and delivery of online learning at any scale. The HTML sanitizer clean_thread_html_body() used for discussion notification emails fails to remove <style> tags from user-generated discussion post content. This content is rendered with Django's |safe template filter in email notification templates, allowing any enrolled student to inject arbitrary CSS into email notifications sent to other users. This enables email tracking (IP address disclosure), content spoofing, and phishing attacks. This vulnerability is fixed with commit cddc25cd791bb78f76833896e4778f668861df12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42857.json
- https://github.com/openedx/openedx-platform/security/advisories/GHSA-4xv3-5j4x-q8g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42857
- https://github.com/openedx/openedx-platform/commit/cddc25cd791bb78f76833896e4778f668861df12
