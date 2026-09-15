# [M] CVE-2025-67809

## Summary
Severity: Medium
Advisory: CVE-2025-67809
CVSS: 4.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-67809
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 10.0 and 10.1. A hardcoded Flickr API key and secret are present in the publicly accessible Flickr Zimlet used by Zimbra Collaboration. Because these credentials are embedded directly in the Zimlet, any unauthorized party could retrieve them and misuse the Flickr integration. An attacker with access to the exposed credentials could impersonate the legitimate application and initiate valid Flickr OAuth flows. If a user is tricked into approving such a request, the attacker could gain access to the user s Flickr data. The hardcoded credentials have since been removed from the Zimlet code, and the associated key has been revoked.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Responsible_Disclosure_Policy
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67809.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67809
