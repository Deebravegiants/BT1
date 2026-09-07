# [M] Traefik incorrectly processes fragment in the URL, leads to Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-fvhj-4qfh-q2hm
CVE: CVE-2023-47106
CWE: CWE-177, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-fvhj-4qfh-q2hm
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.10.6
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.0.0-beta5

## Details
### Summary
When a request is sent to Traefik with a URL fragment, Traefik automatically URL encodes and forwards the fragment to the backend server. This violates the RFC because in the origin-form the URL should only contain the absolute path and the query.

When this is combined with another frontend proxy like Nginx, it can be used to bypass frontend proxy URI-based access control
restrictions. 

### Details
For example, we have this Nginx configuration:

```
location /admin {
     deny all;
     return 403;
}
```
This can be bypassed when the attacker is requesting to /#/../admin

This won’t be vulnerable if the backend server follows the RFC and ignores any characters after the fragment.

However, if Nginx is chained with another reverse proxy which automatically URL encode the character # (Traefik) the URL will become

/%23/../admin

And allow the attacker to completely bypass the Access Restriction from the Nginx Front-End proxy.

Here is a diagram to summarize the attack:

![image](https://user-images.githubusercontent.com/47447167/278849578-34ca0546-99b4-44c8-8fc8-8e799c1f5069.png)

### PoC
![image (1)](https://user-images.githubusercontent.com/47447167/278849597-280f2e80-f2d7-4dd9-9662-b8f488fd5ff2.png)

This is the POC docker I've set up.  It contains Nginx, Traefik proxies and a backend server running PHP.

https://drive.google.com/file/d/1vLnA0g7N7ZKhLNmHmuJ4JJjV_J2akNMt/view?usp=sharing

### Impact
This allows the attacker to completely bypass the Access Restriction from Front-End proxy.

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-fvhj-4qfh-q2hm
- https://nvd.nist.gov/vuln/detail/CVE-2023-47106
- https://datatracker.ietf.org/doc/html/rfc7230#section-5.3.1
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.10.6
- https://github.com/traefik/traefik/releases/tag/v3.0.0-beta5
