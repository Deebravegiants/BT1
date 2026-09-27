# [M] CVE-2022-24682

## Summary
Severity: Medium
Advisory: CVE-2022-24682
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-02-09
Source: https://osv.dev/vulnerability/CVE-2022-24682
Type: osv

## Details
An issue was discovered in the Calendar feature in Zimbra Collaboration Suite 8.8.x before 8.8.15 patch 30 (update 1), as exploited in the wild starting in December 2021. An attacker could place HTML containing executable JavaScript inside element attributes. This markup becomes unescaped, causing arbitrary markup to be injected into the document.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/8.8.15/P30
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-24682
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24682.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-24682
- https://blog.zimbra.com/2022/02/hotfix-available-5-feb-for-zero-day-exploit-vulnerability-in-zimbra-8-8-15/
- https://www.volexity.com/blog/2022/02/03/operation-emailthief-active-exploitation-of-zero-day-xss-vulnerability-in-zimbra/
