# [C] CVE-2018-1117

## Summary
Severity: Critical
Advisory: CVE-2018-1117
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-20
Source: https://osv.dev/vulnerability/CVE-2018-1117
Type: osv

## Details
ovirt-ansible-roles before version 1.0.6 has a vulnerability due to a missing no_log directive, resulting in the 'Add oVirt Provider to ManageIQ/CloudForms' playbook inadvertently disclosing admin passwords in the provisioning log. In an environment where logs are shared with other parties, this could lead to privilege escalation.

## References
- http://www.securityfocus.com/bid/104186
- https://access.redhat.com/errata/RHSA-2018:1452
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1117
