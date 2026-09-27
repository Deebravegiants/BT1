# [M] CVE-2019-10225

## Summary
Severity: Medium
Advisory: CVE-2019-10225
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/CVE-2019-10225
Type: osv

## Details
A flaw was found in atomic-openshift of openshift-4.2 where the basic-user RABC role in OpenShift Container Platform doesn't sufficiently protect the GlusterFS StorageClass against leaking of the restuserkey. An attacker with basic-user permissions is able to obtain the value of restuserkey, and use it to authenticate to the GlusterFS REST service, gaining access to read, and modify files.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1743073
