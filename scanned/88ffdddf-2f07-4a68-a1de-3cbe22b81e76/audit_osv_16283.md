# [M] CVE-2019-3893

## Summary
Severity: Medium
Advisory: CVE-2019-3893
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-3893
Type: osv

## Details
In Foreman it was discovered that the delete compute resource operation, when executed from the Foreman API, leads to the disclosure of the plaintext password or token for the affected compute resource. A malicious user with the "delete_compute_resource" permission can use this flaw to take control over compute resources managed by foreman. Versions before 1.20.3, 1.21.1, 1.22.0 are vulnerable.

## References
- http://www.openwall.com/lists/oss-security/2019/04/14/2
- http://www.securityfocus.com/bid/107846
- https://github.com/theforeman/foreman/pull/6621
- https://projects.theforeman.org/issues/26450
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3893
