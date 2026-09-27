# [M] CVE-2023-34958

## Summary
Severity: Medium
Advisory: CVE-2023-34958
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-34958
Type: osv

## Details
Incorrect access control in Chamilo 1.11.* up to 1.11.18 allows a student subscribed to a given course to download documents belonging to another student if they know the document's ID.

## References
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-109-2023-04-15-Moderate-impact-Moderate-risk-IDOR-in-workstudent-publication
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34958.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34958
- https://github.com/chamilo/chamilo-lms/commit/0c1c29db18856a6f25e21d0405dda2c20b35ff3a
