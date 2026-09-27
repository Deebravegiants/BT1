# [M] CVE-2024-33536

## Summary
Severity: Medium
Advisory: CVE-2024-33536
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-33536
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 9.0 and 10.0. The vulnerability occurs due to inadequate input validation of the res parameter, allowing an authenticated attacker to inject and execute arbitrary JavaScript code within the context of another user's browser session. By uploading a malicious JavaScript file, accessible externally, and crafting a URL containing its location in the res parameter, the attacker can exploit this vulnerability. Subsequently, when another user visits the crafted URL, the malicious JavaScript code is executed.

## References
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.0.8#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P40#Security_Fixes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33536.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33536
