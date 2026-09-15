# [C] CVE-2019-14887

## Summary
Severity: Critical
Advisory: CVE-2019-14887
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2019-14887
Type: osv

## Details
A flaw was found when an OpenSSL security provider is used with Wildfly, the 'enabled-protocols' value in the Wildfly configuration isn't honored. An attacker could target the traffic sent from Wildfly and downgrade the connection to a weaker version of TLS, potentially breaking the encryption. This could lead to a leak of the data being passed over the network. Wildfly version 7.2.0.GA, 7.2.3.GA and 7.2.5.CR2 are believed to be vulnerable.

## References
- https://security.netapp.com/advisory/ntap-20200327-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14887
- https://issues.redhat.com/browse/JBEAP-17965
