# [H] CVE-2019-19343

## Summary
Severity: High
Advisory: CVE-2019-19343
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/CVE-2019-19343
Type: osv

## Details
A flaw was found in Undertow when using Remoting as shipped in Red Hat Jboss EAP before version 7.2.4. A memory leak in HttpOpenListener due to holding remote connections indefinitely may lead to denial of service. Versions before undertow 2.0.25.SP1 and jboss-remoting 5.0.14.SP1 are believed to be vulnerable.

## References
- https://security.netapp.com/advisory/ntap-20220211-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1780445
- https://issues.redhat.com/browse/JBEAP-16695
