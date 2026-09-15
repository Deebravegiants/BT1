# [M] CVE-2018-1002100

## Summary
Severity: Medium
Advisory: CVE-2018-1002100
Aliases: GHSA-2jq6-ffph-p4h8, GO-2023-1959
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-02
Source: https://osv.dev/vulnerability/CVE-2018-1002100
Type: osv

## Details
In Kubernetes versions 1.5.x, 1.6.x, 1.7.x, 1.8.x, and prior to version 1.9.6, the kubectl cp command insecurely handles tar data returned from the container, and can be caused to overwrite arbitrary local files.

## References
- https://github.com/kubernetes/kubernetes/issues/61297
- https://hansmi.ch/articles/2018-04-openshift-s2i-security
- https://bugzilla.redhat.com/show_bug.cgi?id=1564305
