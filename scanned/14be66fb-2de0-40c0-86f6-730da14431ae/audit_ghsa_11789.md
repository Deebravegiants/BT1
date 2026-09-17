# [M] nginx-ui Vulnerable to DoS via Negative Integer Input in Logrotate Interval

## Summary
Severity: Medium
Advisory: GHSA-cp8r-8jvw-v3qg
CVE: CVE-2026-33029
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-cp8r-8jvw-v3qg
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0

## Details
### Summary
An input validation vulnerability in the logrotate configuration allows an authenticated user to cause a complete Denial of Service (DoS). By submitting a negative integer for the rotation interval, the backend enters an infinite loop or an invalid state, rendering the web interface unresponsive.

### Details
The vulnerability exists in the handler for the POST /api/settings endpoint. Specifically, the logrotate.interval field is accepted as a signed integer without lower-bound verification. When a negative value is processed by the backend logic responsible for scheduling or calculating the next rotation, it triggers a non-terminating loop. This consumes CPU resources and prevents the Go web server from handling further concurrent requests.

**Environment:**
- OS: Kali Linux 6.17.10-1kali1 (6.17.10+kali-amd64)
- nginx-ui version: 2.3.3 (513) e5da6dd (go1.26.0 linux/amd64)
- Deployment: Docker container
- Run Command: 
```
docker run -dit \
  --name=nginx-ui \
  --restart=always \
  -v /mnt/user4/appdata/nginx:/etc/nginx \
  -v /mnt/user4/appdata/nginx-ui:/etc/nginx-ui \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 8080:80 -p 8443:443 \
  uozi/nginx-ui:latest
```

### PoC
1. Authenticate to the nginx-ui dashboard.
2. Send a POST request to /api/settings (using Burp Suite, Postman, or curl).
3. Set the payload as follows:
```
.
.
.
{
  "logrotate": {
    "enabled": true,
    "cmd": "logrotate /etc/logrotate.d/nginx",
    "interval": -1
  }
}
.
.
.
```
4. Observe that the web server stops responding to all subsequent requests immediately after the injection.
<img width="1041" height="390" alt="image" src="https://github.com/user-attachments/assets/b746a91a-dd63-4f5e-b1a8-382b9d08e181" />

### Impact
This is a High-availability vulnerability (CWE-20: Improper Input Validation). Any authenticated user with access to settings can permanently hang the service.

A patched version of nginx-ui  is available at https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.4.

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-cp8r-8jvw-v3qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33029
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.4
