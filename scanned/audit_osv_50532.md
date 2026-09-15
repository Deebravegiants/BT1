# [H] CVE-2020-1749

## Summary
Severity: High
Advisory: CVE-2020-1749
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-1749
Type: osv

## Details
A flaw was found in the Linux kernel's implementation of some networking protocols in IPsec, such as VXLAN and GENEVE tunnels over IPv6. When an encrypted tunnel is created between two hosts, the kernel isn't correctly routing tunneled data over the encrypted link; rather sending the data unencrypted. This would allow anyone in between the two endpoints to read the traffic unencrypted. The main threat from this vulnerability is to data confidentiality.

## References
- https://security.netapp.com/advisory/ntap-20201222-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1749
