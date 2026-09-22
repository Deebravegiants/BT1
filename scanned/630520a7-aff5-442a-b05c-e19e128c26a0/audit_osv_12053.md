# [C] CVE-2018-1000861

## Summary
Severity: Critical
Advisory: CVE-2018-1000861
Aliases: GHSA-hhpm-5cp2-hg4x
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-1000861
Type: osv

## Details
A code execution vulnerability exists in the Stapler web framework used by Jenkins 2.153 and earlier, LTS 2.138.3 and earlier in stapler/core/src/main/java/org/kohsuke/stapler/MetaClass.java that allows attackers to invoke some methods on Java objects by accessing crafted URLs that were not intended to be invoked this way.

## References
- http://www.securityfocus.com/bid/106176
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2018-1000861
- http://packetstormsecurity.com/files/166778/Jenkins-Remote-Code-Execution.html
- https://access.redhat.com/errata/RHBA-2019:0024
- https://jenkins.io/security/advisory/2018-12-05/#SECURITY-595
