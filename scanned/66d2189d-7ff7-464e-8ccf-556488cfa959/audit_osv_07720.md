# [M] Apache Tomcat: Delayed cleaning of multi-part upload temporary files may lead to DoS

## Summary
Severity: Medium
Advisory: BIT-tomcat-2025-61795
Aliases: CVE-2025-61795, GHSA-hgrr-935x-pq79
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-tomcat-2025-61795
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.12

## Details
Improper Resource Shutdown or Release vulnerability in Apache Tomcat.

If an error occurred (including exceeding limits) during the processing of a multipart upload, temporary copies of the uploaded parts written to disc were not cleaned up immediately but left for the garbage collection process to delete. Depending on JVM settings, application memory usage and application load, it was possible that space for the temporary copies of uploaded parts would be filled faster than GC cleared it, leading to a DoS.



This issue affects Apache Tomcat: from 11.0.0 through 11.0.11, from 10.1.0 through 10.1.46, from 9.0.0 through 9.0.109.

The following versions were EOL at the time the CVE was created but are 
known to be affected: 8.5.0 though 8.5.100. Other, older, EOL versions may also be affected.
Users are recommended to upgrade to version 11.0.12 or later, 10.1.47 or later or 9.0.110 or later which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/10/27/6
- https://lists.apache.org/thread/wm9mx8brmx9g4zpywm06ryrtvd3160pp
- https://nvd.nist.gov/vuln/detail/CVE-2025-61795
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
