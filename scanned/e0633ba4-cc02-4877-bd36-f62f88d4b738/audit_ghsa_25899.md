# [M] SSRF in repository migration

## Summary
Severity: Medium
Advisory: GHSA-q347-cg56-pcq4
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-14
Source: https://github.com/advisories/GHSA-q347-cg56-pcq4
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.5

## Details
### Impact

The malicious user is able to discover services in the internal network through repository migration functionality. All installations accepting public traffic are affected.

### Patches

Internal network CIDRs are prohibited to be used as repository migration targets. Users should upgrade to 0.12.5 or the latest 0.13.0+dev.

### Workarounds

Run Gogs in its own private network.

### References

https://www.huntr.dev/bounties/327797d7-ae41-498f-9bff-cc0bf98cf531/

### For more information

If you have any questions or comments about this advisory, please post on #6754.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-q347-cg56-pcq4
- https://github.com/gogs/gogs
- https://www.huntr.dev/bounties/327797d7-ae41-498f-9bff-cc0bf98cf531
