# [M] CVE-2020-10715

## Summary
Severity: Medium
Advisory: CVE-2020-10715
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-10715
Type: osv

## Details
A content spoofing vulnerability was found in the openshift/console 3.11 and 4.x. This flaw allows an attacker to craft a URL and inject arbitrary text onto the error page that appears to be from the OpenShift instance. This attack could potentially convince a user that the inserted text is legitimate.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1767665
- https://github.com/openshift/origin-web-console/pull/3173
