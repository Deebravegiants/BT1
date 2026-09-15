# [M] CVE-2017-9378

## Summary
Severity: Medium
Advisory: CVE-2017-9378
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9378
Type: osv

## Details
BigTree CMS through 4.2.18 does not prevent a user from deleting their own account. This could have security relevance because deletion was supposed to be an admin-only action, and the admin may have other tasks (such as data backups) to complete before a user is deleted.

## References
- https://github.com/bigtreecms/BigTree-CMS/commit/f7899701d7be91b7dc546b65e44a27b668eb3b76
- https://github.com/bigtreecms/BigTree-CMS/issues/282
