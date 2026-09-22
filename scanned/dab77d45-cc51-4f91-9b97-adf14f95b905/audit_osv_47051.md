# [M] CVE-2015-8794

## Summary
Severity: Medium
Advisory: CVE-2015-8794
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-01-29
Source: https://osv.dev/vulnerability/CVE-2015-8794
Type: osv

## Details
Absolute path traversal vulnerability in program/steps/addressbook/photo.inc in Roundcube before 1.0.6 and 1.1.x before 1.1.2 allows remote authenticated users to read arbitrary files via a full pathname in the _alt parameter, related to contact photo handling.

## References
- https://roundcube.net/news/2015/06/05/updates-1.1.2-and-1.0.6-released/
- https://roundcube.net/news/2015/06/05/updates-1.1.2-and-1.0.6-released/
- http://trac.roundcube.net/changeset/6ccd4c54b/github
- http://trac.roundcube.net/changeset/e84fafcec/github
- http://trac.roundcube.net/ticket/1490379
