# [M] CVE-2018-16410

## Summary
Severity: Medium
Advisory: CVE-2018-16410
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16410
Type: osv

## Details
Vanilla before 2.6.1 allows SQL injection via an invitationID array to /profile/deleteInvitation, related to applications/dashboard/models/class.invitationmodel.php and applications/dashboard/controllers/class.profilecontroller.php.

## References
- https://open.vanillaforums.com/discussion/36559
- https://hackerone.com/reports/353784
