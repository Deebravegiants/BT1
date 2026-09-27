# [M] CVE-2020-10743

## Summary
Severity: Medium
Advisory: CVE-2020-10743
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2020-10743
Type: osv

## Details
It was discovered that OpenShift Container Platform's (OCP) distribution of Kibana could open in an iframe, which made it possible to intercept and manipulate requests. This flaw allows an attacker to trick a user into performing arbitrary actions in OCP's distribution of Kibana, such as clickjacking.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1834550
