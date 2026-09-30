# [C] CVE-2017-1002101

## Summary
Severity: Critical
Advisory: CVE-2017-1002101
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2017-1002101
Type: osv

## Details
In Kubernetes versions 1.3.x, 1.4.x, 1.5.x, 1.6.x and prior to versions 1.7.14, 1.8.9 and 1.9.4 containers using subpath volume mounts with any volume type (including non-privileged pods, subject to file permissions) can access files/directories outside of the volume, including the host's filesystem.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00041.html
- https://access.redhat.com/errata/RHSA-2018:0475
- https://github.com/kubernetes/kubernetes/issues/60813
- https://github.com/bgeesaman/subpath-exploit/
