# [M] operator-sdk: privilege escalation due to incorrect permissions of /etc/passwd

## Summary
Severity: Medium
Advisory: GHSA-856v-8qm2-9wjv
CVE: CVE-2025-7195
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2025-08-07
Source: https://github.com/advisories/GHSA-856v-8qm2-9wjv
Type: github-advisory

## Affected
- Go: `github.com/operator-framework/operator-sdk` — affected >=0 <0.15.2

## Details
Early versions of Operator-SDK provided an insecure method to allow operator containers to run in environments that used a random UID. Operator-SDK before 0.15.2 provided a script, user_setup, which modifies the permissions of the /etc/passwd file to 664 during build time. Developers who used Operator-SDK before 0.15.2 to scaffold their operator may still be impacted by this if the insecure user_setup script is still being used to build new container images. In affected images, the /etc/passwd file was created during build time with group-writable permissions and a group ownership of root (gid=0). An attacker who can execute commands within an affected container, even as a non-root user, may be able to leverage their membership in the root group to modify the /etc/passwd file. This could allow the attacker to add a new user with any arbitrary UID, including UID 0, leading to full root privileges within the container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7195
- https://github.com/operator-framework/operator-sdk
- https://bugzilla.redhat.com/show_bug.cgi?id=2376300
- https://access.redhat.com/security/cve/CVE-2025-7195
- https://access.redhat.com/errata/RHSA-2026:5633
- https://access.redhat.com/errata/RHSA-2026:2572
- https://access.redhat.com/errata/RHSA-2026:0737
- https://access.redhat.com/errata/RHSA-2026:0722
- https://access.redhat.com/errata/RHSA-2026:0718
- https://access.redhat.com/errata/RHSA-2026:0627
- https://access.redhat.com/errata/RHSA-2025:23542
- https://access.redhat.com/errata/RHSA-2025:23529
- https://access.redhat.com/errata/RHSA-2025:23528
- https://access.redhat.com/errata/RHSA-2025:22684
- https://access.redhat.com/errata/RHSA-2025:22683
- https://access.redhat.com/errata/RHSA-2025:22420
- https://access.redhat.com/errata/RHSA-2025:22418
- https://access.redhat.com/errata/RHSA-2025:22416
- https://access.redhat.com/errata/RHSA-2025:22415
- https://access.redhat.com/errata/RHSA-2025:21885
