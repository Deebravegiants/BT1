# [H] CVE-2016-7075

## Summary
Severity: High
Advisory: CVE-2016-7075
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2016-7075
Type: osv

## Details
It was found that Kubernetes as used by Openshift Enterprise 3 did not correctly validate X.509 client intermediate certificate host name fields. An attacker could use this flaw to bypass authentication requirements by using a specially crafted X.509 certificate.

## References
- https://access.redhat.com/errata/RHSA-2016:2064
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7075
- https://github.com/kubernetes/kubernetes/issues/34517
