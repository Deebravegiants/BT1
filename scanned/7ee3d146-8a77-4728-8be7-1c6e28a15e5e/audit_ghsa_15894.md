# [M] Eclipse Jetty has a denial of service vulnerability on DosFilter

## Summary
Severity: Medium
Advisory: GHSA-j26w-f9rq-mr2q
CVE: CVE-2024-9823
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-j26w-f9rq-mr2q
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty.ee10:jetty-ee10-servlets` — affected >=12.0.0 <12.0.3
- Maven: `org.eclipse.jetty.ee8:jetty-ee8-servlets` — affected >=12.0.0 <12.0.3
- Maven: `org.eclipse.jetty.ee9:jetty-ee9-servlets` — affected >=12.0.0 <12.0.3
- Maven: `org.eclipse.jetty:jetty-servlets` — affected >=9.0.0 <9.4.54
- Maven: `org.eclipse.jetty:jetty-servlets` — affected >=10.0.0 <10.0.18
- Maven: `org.eclipse.jetty:jetty-servlets` — affected >=11.0.0 <11.0.18

## Details
Description
There exists a security vulnerability in Jetty's DosFilter which can be exploited by unauthorized users to cause remote denial-of-service (DoS) attack on the server using DosFilter. By repeatedly sending crafted requests, attackers can trigger OutofMemory errors and exhaust the server's memory finally.


Vulnerability details
The Jetty DoSFilter (Denial of Service Filter) is a security filter designed to protect web applications against certain types of Denial of Service (DoS) attacks and other abusive behavior. It helps to mitigate excessive resource consumption by limiting the rate at which clients can make requests to the server.  The DoSFilter monitors and tracks client request patterns, including request rates, and can take actions such as blocking or delaying requests from clients that exceed predefined thresholds.  The internal tracking of requests in DoSFilter is the source of this OutOfMemory condition.


Impact
Users of the DoSFilter may be subject to DoS attacks that will ultimately exhaust the memory of the server if they have not configured session passivation or an aggressive session inactivation timeout.


Patches
The DoSFilter has been patched in all active releases to no longer support the session tracking mode, even if configured.


Patched releases:

  *  9.4.54
  *  10.0.18
  *  11.0.18
  *  12.0.3

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-7hcf-ppf8-5w5h
- https://nvd.nist.gov/vuln/detail/CVE-2024-9823
- https://github.com/jetty/jetty.project/issues/1256
- https://github.com/jetty/jetty.project
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/39
- https://lists.debian.org/debian-lts-announce/2025/04/msg00001.html
- https://security.netapp.com/advisory/ntap-20250306-0006
