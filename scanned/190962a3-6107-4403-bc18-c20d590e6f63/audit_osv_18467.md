# [M] CVE-2020-27816

## Summary
Severity: Medium
Advisory: CVE-2020-27816
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-27816
Type: osv

## Details
The elasticsearch-operator does not validate the namespace where kibana logging resource is created and due to that it is possible to replace the original openshift-logging console link (kibana console) to different one, created based on the new CR for the new kibana resource. This could lead to an arbitrary URL redirection or the openshift-logging console link damage. This flaw affects elasticsearch-operator-container versions before 4.7.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1902698
