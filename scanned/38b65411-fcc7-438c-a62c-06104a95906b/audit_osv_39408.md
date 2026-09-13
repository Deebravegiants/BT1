# [H] Roxy-WI: Authenticated RCE via 'configver' URL parameter (os.system sink in /config/versions/.../save)

## Summary
Severity: High
Advisory: CVE-2026-45564
Aliases: GHSA-w42x-3v8j-cmg2
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45564
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, POST /config/versions/<service>/<server_ip>/<configver>/save interpolates the URL-path configver parameter directly into a config-version path that ends up at os.system(f"dos2unix -q {cfg}"). configver is not run through EscapedString (Pydantic doesn't validate path segments declared as str) and the surrounding .. block is the broken tuple-membership patch from GHSA-vapt-004. An authenticated user with role <= 3 ("user") therefore reaches a bin/sh -c command-injection sink. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45564.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-w42x-3v8j-cmg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45564
