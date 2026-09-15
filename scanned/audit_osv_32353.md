# [M] CVE-2025-27914

## Summary
Severity: Medium
Advisory: CVE-2025-27914
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-27914
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 9.0 and 10.0 and 10.1. A Reflected Cross-Site Scripting (XSS) vulnerability exists in the /h/rest endpoint, allowing authenticated attackers to inject and execute arbitrary JavaScript in a victim's session. Exploitation requires a valid auth token and involves a crafted URL with manipulated query parameters that triggers XSS when accessed by a victim.

## References
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.0.11#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Responsible_Disclosure_Policy
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27914.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27914
