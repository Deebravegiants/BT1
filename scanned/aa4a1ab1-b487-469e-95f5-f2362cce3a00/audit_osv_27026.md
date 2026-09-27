# [C] SSRF on AWS deployed instances of AnythingLLM via /metadata

## Summary
Severity: Critical
Advisory: CVE-2024-0455
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-02-25
Source: https://osv.dev/vulnerability/CVE-2024-0455
Type: osv

## Details
The inclusion of the web scraper for AnythingLLM means that any user with the proper authorization level (manager, admin, and when in single user) could put in the URL
```
http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance
```
which is a special IP and URL that resolves only when the request comes from within an EC2 instance. This would allow the user to see the connection/secret credentials for their specific instance and be able to manage it regardless of who deployed it.

The user would have to have pre-existing knowledge of the hosting infra which the target instance is deployed on, but if sent - would resolve if on EC2 and the proper `iptable` or firewall rule is not configured for their setup.

## References
- https://huntr.com/bounties/07d83b49-7ebb-40d2-83fc-78381e3c5c9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0455.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0455
- https://github.com/mintplex-labs/anything-llm/commit/b2b2c2afe15c48952d57b4d01e7108f9515c5f55
