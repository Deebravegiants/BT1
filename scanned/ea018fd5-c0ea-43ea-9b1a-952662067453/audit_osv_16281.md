# [M] CVE-2019-3886

## Summary
Severity: Medium
Advisory: CVE-2019-3886
CVSS: 5.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2019-04-04
Source: https://osv.dev/vulnerability/CVE-2019-3886
Type: osv

## Details
An incorrect permissions check was discovered in libvirt 4.8.0 and above. The readonly permission was allowed to invoke APIs depending on the guest agent, which could lead to potentially disclosing unintended information or denial of service by causing libvirt to block.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CYMNKXAUBZCFBBPFH64FJPH5EJH4GSU2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R5DHYIFECZ7BMVXK4EP4FDFZXK7I5MZH/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00105.html
- http://www.securityfocus.com/bid/107777
- https://access.redhat.com/errata/RHBA-2019:3723
- https://usn.ubuntu.com/4021-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3886
