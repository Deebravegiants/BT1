# [M] CVE-2017-15137

## Summary
Severity: Medium
Advisory: CVE-2017-15137
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/CVE-2017-15137
Type: osv

## Details
The OpenShift image import whitelist failed to enforce restrictions correctly when running commands such as "oc tag", for example. This could allow a user with access to OpenShift to run images from registries that should not be allowed.

## References
- https://access.redhat.com/errata/RHBA-2018:0489
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-15137
