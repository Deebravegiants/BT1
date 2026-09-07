# [M] Astro's `X-Forwarded-Host` is reflected without validation

## Summary
Severity: Medium
Advisory: GHSA-5ff5-9fcw-vg88
CVE: CVE-2025-61925
CWE: CWE-20, CWE-470
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-5ff5-9fcw-vg88
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <5.14.3

## Details
### Summary
When running Astro in on-demand rendering mode using a adapter such as the node adapter it is possible to maliciously send an `X-Forwarded-Host` header that is reflected when using the recommended `Astro.url` property as there is no validation that the value is safe.

### Details
Astro reflects the value in `X-Forwarded-Host` in output when using `Astro.url` without any validation. 

It is common for web servers such as nginx to route requests via the `Host` header, and forward on other request headers. As such as malicious request can be sent with both a `Host` header and an `X-Forwarded-Host` header where the values do not match and the `X-Forwarded-Host` header is malicious. Astro will then return the malicious value.

This could result in any usages of the `Astro.url` value in code being manipulated by a request. For example if a user follows guidance and uses `Astro.url` for a canonical link the canonical link can be manipulated to another site. It is not impossible to imagine that the value could also be used as a login/registration or other form URL as well, resulting in potential redirecting of login credentials to a malicious party.

As this is a per-request attack vector the surface area would only be to the malicious user until one considers that having a caching proxy is a common setup, in which case any page which is cached could persist the malicious value for subsequent users.

Many other frameworks have an allowlist of domains to validate against, or do not have a case where the headers are reflected to avoid such issues.

### PoC
- Check out the minimal Astro example found here: https://github.com/Chisnet/minimal_dynamic_astro_server
- `nvm use`
- `yarn run build`
- `node ./dist/server/entry.mjs`
- `curl --location 'http://localhost:4321/' --header 'X-Forwarded-Host: www.evil.com' --header 'Host: www.example.com'`
- Observe that the response reflects the malicious `X-Forwarded-Host` header

For the more advanced / dangerous attack vector deploy the application behind a caching proxy, e.g. Cloudflare, set a non-zero cache time, perform the above `curl` request a few times to establish a cache, then perform the request without the malicious headers and observe that the malicious data is persisted.

### Impact

This could affect anyone using Astro in an on-demand/dynamic rendering mode behind a caching proxy.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-5ff5-9fcw-vg88
- https://nvd.nist.gov/vuln/detail/CVE-2025-61925
- https://github.com/withastro/astro/commit/6ee63bfac4856f21b4d4633021b3d2ee059e553f
- https://github.com/Chisnet/minimal_dynamic_astro_server
- https://github.com/withastro/astro
