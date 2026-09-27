# [M] CVE-2016-3111

## Summary
Severity: Medium
Advisory: CVE-2016-3111
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/CVE-2016-3111
Type: osv

## Details
pulp.spec in the installation process for Pulp 2.8.3 generates the RSA key pairs used to validate messages between the pulp server and pulp consumers in a directory that is world-readable before later modifying the permissions, which might allow local users to read the generated RSA keys via reading the key files while the installation process is running.

## References
- http://www.openwall.com/lists/oss-security/2016/05/20/1
- https://access.redhat.com/errata/RHBA-2016:1501
- https://bugzilla.redhat.com/attachment.cgi?id=1146522
- http://pkgs.fedoraproject.org/cgit/rpms/pulp.git/tree/pulp.spec#n317
- http://pkgs.fedoraproject.org/cgit/rpms/pulp.git/tree/pulp.spec#n620
- https://bugzilla.redhat.com/show_bug.cgi?id=1326251
- https://github.com/pulp/pulp/blob/master/pulp.spec#L473-L486
- https://github.com/pulp/pulp/blob/master/pulp.spec#L894-L903
- https://pulp.plan.io/issues/1837
