# [H] CVE-2018-1080

## Summary
Severity: High
Advisory: CVE-2018-1080
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-1080
Type: osv

## Details
Dogtag PKI, through version 10.6.1, has a vulnerability in AAclAuthz.java that, under certain configurations, causes the application of ACL allow and deny rules to be reversed. If a server is configured to process allow rules before deny rules (authz.evaluateOrder=allow,deny), then allow rules will deny access and deny rules will grant access. This may result in an escalation of privileges or have other unintended consequences.

## References
- https://access.redhat.com/errata/RHSA-2018:1979
- https://pagure.io/freeipa/issue/7453
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1080
- https://review.gerrithub.io/c/dogtagpki/pki/+/404435
