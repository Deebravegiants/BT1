# [H] CVE-2019-3782

## Summary
Severity: High
Advisory: CVE-2019-3782
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-13
Source: https://osv.dev/vulnerability/CVE-2019-3782
Type: osv

## Details
Cloud Foundry CredHub CLI, versions prior to 2.2.1, inadvertently writes authentication credentials provided via environment variables to its persistent config file. A local authenticated malicious user with access to the CredHub CLI config file can use these credentials to retrieve and modify credentials stored in CredHub that are authorized to the targeted user.

## References
- http://www.securityfocus.com/bid/107038
- https://www.cloudfoundry.org/blog/cve-2019-3782
