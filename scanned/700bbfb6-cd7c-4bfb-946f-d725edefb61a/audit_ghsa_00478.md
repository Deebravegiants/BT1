# [C] Apache Struts 2.0.1 uses an unintentional expression in a Freemarker tag instead of string literal

## Summary
Severity: Critical
Advisory: GHSA-8fx9-5hx8-crhm
CVE: CVE-2017-12611
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-8fx9-5hx8-crhm
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.1 <2.3.34
- Maven: `org.apache.struts:struts2-core` — affected >=2.5.0 <2.5.11

## Details
In Apache Struts 2.0.1 through 2.3.33 and 2.5 through 2.5.10.1, using an unintentional expression in a Freemarker tag instead of string literals can lead to a RCE attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12611
- https://github.com/apache/struts/commit/2306f5f7fad7f0157f216f34331238feb0539fa
- https://github.com/apache/struts/commit/637ad1c3707266c33daabb18d7754e795e6681f
- https://github.com/apache/struts
- https://kb.netapp.com/support/s/article/ka51A000000CgttQAC/NTAP-20170911-0001
- https://struts.apache.org/docs/s2-053.html
- https://web.archive.org/web/20170923161654/http://www.securityfocus.com/bid/100829
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2017-003.txt
- http://www.oracle.com/technetwork/security-advisory/alert-cve-2017-9805-3889403.html
