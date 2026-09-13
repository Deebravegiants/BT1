# [H] CVE-2025-68645

## Summary
Severity: High
Advisory: CVE-2025-68645
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2025-68645
Type: osv

## Details
A Local File Inclusion (LFI) vulnerability exists in the Webmail Classic UI of Zimbra Collaboration (ZCS) 10.0 and 10.1 because of improper handling of user-supplied request parameters in the RestFilter servlet. An unauthenticated remote attacker can craft requests to the /h/rest endpoint to influence internal request dispatching, allowing inclusion of arbitrary files from the WebRoot directory.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Responsible_Disclosure_Policy
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-68645
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68645.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68645
