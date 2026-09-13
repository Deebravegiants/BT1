# [M] CVE-2019-1000017

## Summary
Severity: Medium
Advisory: CVE-2019-1000017
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-1000017
Type: osv

## Details
Chamilo Chamilo-lms version 1.11.8 and earlier contains an Incorrect Access Control vulnerability in Tickets component that can result in an authenticated user can read all tickets available on the platform, due to lack of access controls. This attack appears to be exploitable via ticket_id=[ticket number]. This vulnerability appears to have been fixed in 1.11.x after commit 33e2692a37b5b6340cf5bec1a84e541460983c03.

## References
- https://github.com/chamilo/chamilo-lms/commit/33e2692a37b5b6340cf5bec1a84e541460983c03
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-34-2019-01-14-Moderate-risk-moderate-impact-XSS-and-unauthorized-access
