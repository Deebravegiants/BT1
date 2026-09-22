# [H] CVE-2022-4055

## Summary
Severity: High
Advisory: CVE-2022-4055
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2022-11-18
Source: https://osv.dev/vulnerability/CVE-2022-4055
Type: osv

## Details
When xdg-mail is configured to use thunderbird for mailto URLs, improper parsing of the URL can lead to additional headers being passed to thunderbird that should not be included per RFC 2368. An attacker can use this method to create a mailto URL that looks safe to users, but will actually attach files when clicked.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4055.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4055
- https://gitlab.freedesktop.org/xdg/xdg-utils/-/issues/205#note_1494267
