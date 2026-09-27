# [M] CVE-2020-15412

## Summary
Severity: Medium
Advisory: CVE-2020-15412
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-15412
Type: osv

## Details
An issue was discovered in MISP 2.4.128. app/Controller/EventsController.php lacks an event ACL check before proceeding to allow a user to send an event contact form.

## References
- https://github.com/MISP/MISP/commit/b0be3b07fee2ab9bf1869ef81a7f24f58bd687ef
