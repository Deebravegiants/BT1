# [H] Silverstripe X-Forwarded-Host request hostname injection

## Summary
Severity: High
Advisory: GHSA-25gq-jvx2-vg9x
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-25gq-jvx2-vg9x
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.13

## Details
A potential hostname injection vulnerability has been found which could allow attackers to alter url resolution.

If a request contains the X-Forwarded-Host HTTP header a website would then use its value in place of the actual HTTP hostname. In cases where caching is enabled, this could allow an attacker to potentially embed a remote url as the base_url for any site. This would then cause other visitors to the site to be redirected unknowingly.

This header is necessary for servers running behind a reverse proxy (such as nginx). Such servers are likely not vulnerable to this risk.

A fix has been merged into the default installer, although existing projects which do not run behind a reverse proxy should update their htaccess as below:
```
<IfModule mod_headers.c>
    # Remove X-Forwarded-Host header sent as a part of any request from the web
    RequestHeader unset X-Forwarded-Host
</IfModule>
```

## References
- https://github.com/silverstripe/silverstripe-framework/commit/75137dbab28c0efd28b07e50044a50c5af4e46aa
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-013-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-013
