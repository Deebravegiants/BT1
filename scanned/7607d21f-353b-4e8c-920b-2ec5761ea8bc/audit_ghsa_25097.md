# [C] Jasig Java CAS Client, .NET CAS Client, and phpCAS contain URL parameter injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9fc5-q25c-r2wr
CVE: CVE-2014-4172
CWE: CWE-74
Ecosystem: Maven, NuGet, Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9fc5-q25c-r2wr
Type: github-advisory

## Affected
- NuGet: `DotNetCasClient` — affected >=0 <1.0.2
- Maven: `org.jasig.cas:cas-client` — affected >=0 <3.3.2
- Packagist: `jasig/phpcas` — affected >=0 <1.3.3

## Details
A URL parameter injection vulnerability was found in the back-channel ticket validation step of the CAS protocol in Jasig Java CAS Client before 3.3.2, .NET CAS Client before 1.0.2, and phpCAS before 1.3.3 that allow remote attackers to inject arbitrary web script or HTML via the (1) service parameter to validation/AbstractUrlBasedTicketValidator.java or (2) pgtUrl parameter to validation/Cas20ServiceTicketValidator.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4172
- https://github.com/Jasig/phpCAS/pull/125
- https://github.com/Jasig/dotnet-cas-client/commit/f0e030014fb7a39e5f38469f43199dc590fd0e8d
- https://github.com/Jasig/java-cas-client/commit/ae37092100c8eaec610dab6d83e5e05a8ee58814
- https://github.com/apereo/java-cas-client/commit/266eba7c2d870d70caba6f41576d19f2fcc869b1
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=759718
- https://bugzilla.redhat.com/show_bug.cgi?id=1131350
- https://exchange.xforce.ibmcloud.com/vulnerabilities/95673
- https://github.com/Jasig/phpCAS/blob/master/docs/ChangeLog
- https://issues.jasig.org/browse/CASC-228
- https://www.debian.org/security/2014/dsa-3017.en.html
- https://www.mail-archive.com/cas-user@lists.jasig.org/msg17338.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-August/137182.html
