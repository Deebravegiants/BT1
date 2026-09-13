# [H] Server-Side Request Forgery in gogs webhook

## Summary
Severity: High
Advisory: GHSA-w689-557m-2cvq
CVE: CVE-2022-1285
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-w689-557m-2cvq
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.8

## Details
### Impact

The malicious user is able to discover services in the internal network through webhook functionality. All installations accepting public traffic are affected.

### Patches

Webhook payload URLs are revalidated before each delivery to make sure they are not resolved to blocked local network addresses. Users should upgrade to 0.12.8 or the latest 0.13.0+dev.

### Workarounds

Run Gogs in its own private network.

### References

https://huntr.dev/bounties/da1fbd6e-7a02-458e-9c2e-6d226c47046d/

### For more information

If you have any questions or comments about this advisory, please post on https://github.com/gogs/gogs/issues/6901.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-w689-557m-2cvq
- https://nvd.nist.gov/vuln/detail/CVE-2022-1285
- https://github.com/gogs/gogs/commit/7885f454a4946c4bbec1b4f8c603b5eea7429c7f
- https://github.com/gogs/gogs
- https://huntr.dev/bounties/da1fbd6e-7a02-458e-9c2e-6d226c47046d
