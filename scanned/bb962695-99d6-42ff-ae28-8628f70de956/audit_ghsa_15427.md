# [H] Pulp incorrectly assigns RBAC permissions in tasks that create objects

## Summary
Severity: High
Advisory: GHSA-9m5j-4xx9-44j9
CVE: CVE-2024-7143
CWE: CWE-277
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-08-07
Source: https://github.com/advisories/GHSA-9m5j-4xx9-44j9
Type: github-advisory

## Affected
- PyPI: `pulpcore` — affected >=0

## Details
A flaw was found in the Pulp package. When a role-based access control (RBAC) object in Pulp is set to assign permissions on its creation, it uses the `AutoAddObjPermsMixin` (typically the add_roles_for_object_creator method). This method finds the object creator by checking the current authenticated user. For objects that are created within a task, this current user is set by the first user with any permissions on the task object. This means the oldest user with model/domain-level task permissions will always be set as the current user of a task, even if they didn't dispatch the task. Therefore, all objects created in tasks will have their permissions assigned to this oldest user, and the creating user will receive nothing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7143
- https://access.redhat.com/errata/RHSA-2024:6765
- https://access.redhat.com/security/cve/CVE-2024-7143
- https://bugzilla.redhat.com/show_bug.cgi?id=2300125
- https://github.com/pulp/pulpcore
- https://github.com/pulp/pulpcore/blob/93f241f34c503da0fbac94bdba739feda2636e12/pulpcore/tasking/_util.py#L108
- https://github.com/pulp/pulpcore/blob/main/CHANGES.md
