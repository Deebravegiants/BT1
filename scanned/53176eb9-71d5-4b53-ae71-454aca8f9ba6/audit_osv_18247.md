# [H] CVE-2020-25636

## Summary
Severity: High
Advisory: CVE-2020-25636
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-10-05
Source: https://osv.dev/vulnerability/CVE-2020-25636
Type: osv

## Details
A flaw was found in Ansible Base when using the aws_ssm connection plugin as there is no namespace separation for file transfers. Files are written directly to the root bucket, making possible to have collisions when running multiple ansible processes. This issue affects mainly the service availability.

## References
- https://github.com/ansible-collections/community.aws/issues/221
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-25636
