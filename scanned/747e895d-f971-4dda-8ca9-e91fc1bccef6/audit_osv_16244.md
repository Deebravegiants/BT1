# [H] CVE-2019-3818

## Summary
Severity: High
Advisory: CVE-2019-3818
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/CVE-2019-3818
Type: osv

## Details
The kube-rbac-proxy container before version 0.4.1 as used in Red Hat OpenShift Container Platform does not honor TLS configurations, allowing for use of insecure ciphers and TLS 1.0. An attacker could target traffic sent over a TLS connection with a weak configuration and potentially break the encryption.

## References
- http://www.securityfocus.com/bid/106744
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/security/cve/CVE-2019-3818
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3818
