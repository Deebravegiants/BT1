# [H] Kiwi TCMS's misconfigured HTTP headers allow stored XSS execution with Firefox

## Summary
Severity: High
Advisory: GHSA-jpgw-2r9m-8qfw
CVE: CVE-2023-36809
CWE: CWE-434, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-jpgw-2r9m-8qfw
Type: github-advisory

## Affected
- PyPI: `kiwitcms` — affected >=0 <12.5

## Details
### Impact

Kiwi TCMS allows users to upload attachments to test plans, test cases, etc. Earlier versions of Kiwi TCMS had introduced
changes which were meant to serve all uploaded files as plain text in order to prevent browsers from executing potentially dangerous files when such files are accessed directly! 

The previous Nginx configuration was incorrect allowing certain browsers like Firefox to ignore the `Content-Type: text/plain` header on some occasions thus allowing potentially dangerous scripts to be executed. 

Additionally file upload validators and parts of the HTML rendering code have been found to require additional sanitation and improvements.

### Patches

- Updated Nginx content type configuration
- Improved file upload validation code to prevent more potentially dangerous uploads
- Sanitization of test plan names used in the `tree_view_html()` function

### References

Disclosed by [M Nadeem Qazi](https://huntr.dev/bounties/511489dd-ba38-4806-9029-b28ab2830aa8/) and
[Mahshooq Zubair](https://huntr.dev/bounties/c6eeb346-fa99-4d41-bc40-b68f8d689223/).

## References
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-jpgw-2r9m-8qfw
- https://nvd.nist.gov/vuln/detail/CVE-2023-36809
- https://github.com/kiwitcms/kiwi/commit/195ea53eaaf360c19227c864cc0fe58910032c3c
- https://github.com/kiwitcms/kiwi/commit/ffb00450be52fe11a82a2507632c2328cae4ec9d
- https://github.com/kiwitcms/Kiwi
- https://huntr.dev/bounties/511489dd-ba38-4806-9029-b28ab2830aa8
- https://huntr.dev/bounties/c6eeb346-fa99-4d41-bc40-b68f8d689223
- https://kiwitcms.org/blog/kiwi-tcms-team/2023/07/04/kiwi-tcms-125
- https://www.github.com/kiwitcms/kiwi/commit/195ea53eaaf360c19227c864cc0fe58910032c3c
- https://www.github.com/kiwitcms/kiwi/commit/ffb00450be52fe11a82a2507632c2328cae4ec9d
