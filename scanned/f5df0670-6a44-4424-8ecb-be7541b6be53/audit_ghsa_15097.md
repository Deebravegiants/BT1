# [H] aiohttp is vulnerable to directory traversal

## Summary
Severity: High
Advisory: GHSA-5h86-8mv2-jq9f
CVE: CVE-2024-23334
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-29
Source: https://github.com/advisories/GHSA-5h86-8mv2-jq9f
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=1.0.5 <3.9.2

## Details
### Summary
Improperly configuring static resource resolution in aiohttp when used as a web server can result in the unauthorized reading of arbitrary files on the system.

### Details
When using aiohttp as a web server and configuring static routes, it is necessary to specify the root path for static files. Additionally, the option 'follow_symlinks' can be used to determine whether to follow symbolic links outside the static root directory. When 'follow_symlinks' is set to True, there is no validation to check if a given file path is within the root directory.This can lead to directory traversal vulnerabilities, resulting in unauthorized access to arbitrary files on the system, even when symlinks are not present.

i.e. An application is only vulnerable with setup code like:
```
app.router.add_routes([
    web.static("/static", "static/", follow_symlinks=True),  # Remove follow_symlinks to avoid the vulnerability
])
```

### Impact
This is a directory traversal vulnerability with CWE ID 22. When using aiohttp as a web server and enabling static resource resolution with `follow_symlinks` set to True, it can lead to this vulnerability. This vulnerability has been present since the introduction of the `follow_symlinks` parameter.

### Workaround
Even if upgrading to a patched version of aiohttp, we recommend following these steps regardless.

If using `follow_symlinks=True` outside of a restricted local development environment, disable the option immediately. This option is NOT needed to follow symlinks which point to a location _within_ the static root directory, it is _only_ intended to allow a symlink to break out of the static directory. Even with this CVE fixed, there is still a substantial risk of misconfiguration when using this option on a server that accepts requests from remote users.

Additionally, aiohttp has always recommended using a reverse proxy server (such as nginx) to handle static resources and _not_ to use these static resources in aiohttp for production environments. Doing so also protects against this vulnerability, and is why we expect the number of affected users to be very low.

-----

Patch: https://github.com/aio-libs/aiohttp/pull/8079/files

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-5h86-8mv2-jq9f
- https://nvd.nist.gov/vuln/detail/CVE-2024-23334
- https://github.com/aio-libs/aiohttp/pull/8079
- https://github.com/aio-libs/aiohttp/pull/8079/files
- https://github.com/aio-libs/aiohttp/commit/1c335944d6a8b1298baf179b7c0b3069f10c514b
- https://github.com/aio-libs/aiohttp
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp/PYSEC-2024-24.yaml
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ICUOCFGTB25WUT336BZ4UNYLSZOUVKBD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XXWVZIVAYWEBHNRIILZVB3R3SDQNNAA7
- https://www.exploit-db.com/exploits/52474
