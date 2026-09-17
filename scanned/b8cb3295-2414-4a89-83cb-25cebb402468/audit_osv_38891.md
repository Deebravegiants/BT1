# [H] CVE-2026-43001

## Summary
Severity: High
Advisory: CVE-2026-43001
Aliases: GHSA-hhq2-3832-xxcv, PYSEC-2026-602
CVSS: 7.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43001
Type: osv

## Details
An issue was discovered in OpenStack Keystone before 29.0.2. POST /v3/credentials did not validate that the caller-supplied project_id for an EC2-type credential matched the project of the authenticating application credential. This allowed an attacker holding an unrestricted application credential for project A to create an EC2 credential targeting project B; a subsequent /v3/ec2tokens exchange would then issue a Keystone token scoped to project B while still carrying the original app_cred_id, enabling cross-project lateral movement within the credential owner's role footprint.

## References
- https://bugs.launchpad.net/keystone/+bug/2149775
- https://review.opendev.org/c/openstack/keystone/+/985804
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43001.json
- https://security.openstack.org/ossa/OSSA-2026-015.html
- https://access.redhat.com/errata/RHSA-2026:39808
- https://access.redhat.com/errata/RHSA-2026:54757
- https://access.redhat.com/security/cve/CVE-2026-43001
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43001.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43001
- https://bugzilla.redhat.com/show_bug.cgi?id=2464305
