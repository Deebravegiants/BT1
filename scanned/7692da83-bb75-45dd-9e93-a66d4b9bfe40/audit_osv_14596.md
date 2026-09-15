# [M] CVE-2019-10198

## Summary
Severity: Medium
Advisory: CVE-2019-10198
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-10198
Type: osv

## Details
An authentication bypass vulnerability was discovered in foreman-tasks before 0.15.7. Previously, commit tasks were searched through find_resource, which performed authorization checks. After the change to Foreman, an unauthenticated user can view the details of a task through the web UI or API, if they can discover or guess the UUID of the task.

## References
- https://access.redhat.com/errata/RHSA-2019:3172
- https://projects.theforeman.org/issues/27275
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10198
