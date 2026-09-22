# [M] CVE-2017-8039

## Summary
Severity: Medium
Advisory: CVE-2017-8039
Aliases: GHSA-q4v9-qjmw-j7vf
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-8039
Type: osv

## Details
An issue was discovered in Pivotal Spring Web Flow through 2.4.5. Applications that do not change the value of the MvcViewFactoryCreator useSpringBinding property which is disabled by default (i.e., set to 'false') can be vulnerable to malicious EL expressions in view states that process form submissions but do not have a sub-element to declare explicit data binding property mappings. NOTE: this issue exists because of an incomplete fix for CVE-2017-4971.

## References
- http://www.securityfocus.com/bid/100849
- https://pivotal.io/security/cve-2017-8039
