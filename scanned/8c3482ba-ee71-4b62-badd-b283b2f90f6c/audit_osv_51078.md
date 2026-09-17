# [M] CVE-2021-20201

## Summary
Severity: Medium
Advisory: CVE-2021-20201
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-20201
Type: osv

## Details
A flaw was found in spice in versions before 0.14.92. A DoS tool might make it easier for remote attackers to cause a denial of service (CPU consumption) by performing many renegotiations within a single connection.

## References
- https://security.gentoo.org/glsa/202208-10
- https://bugzilla.redhat.com/show_bug.cgi?id=1921846
- https://blog.qualys.com/product-tech/2011/10/31/tls-renegotiation-and-denial-of-service-attacks
