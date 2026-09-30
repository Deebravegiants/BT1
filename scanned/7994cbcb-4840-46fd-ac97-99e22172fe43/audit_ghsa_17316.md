# [M] Misskey has a login rate limit bypass via spoofed X-Forwarded-For header

## Summary
Severity: Medium
Advisory: GHSA-wwrj-3hvj-prpm
CVE: CVE-2025-66482
CWE: CWE-1188, CWE-307
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-wwrj-3hvj-prpm
Type: github-advisory

## Affected
- npm: `misskey-js` — affected >=2025.9.1 <2025.12.0-alpha.2

## Details
### Summary
When using an untrusted reverse proxy or not using a reverse proxy at all, attackers can bypass IP rate limiting by adding a forged X-Forwarded-For header. Starting with version 2025.9.1, an option (`trustProxy`) has been added in config file to prevent this from happening. However, it is initialized with an insecure default value before version 2025.12.0, making it still vulnerable if the configuration is not set correctly.

### Workaround

If you are running Misskey with a trusted reverse proxy, you should *not* be affected by this vulnerability.

- There is no workaround for the Misskey itself. Please update Misskey to the latest version or set up a trusted reverse proxy.
- From v2025.9.1 to v2025.11.1, workaround is available. Set `trustProxy: false` in config file.
- This is patched in v2025.12.0 by flipping default value of `trustProxy` to `false`. If you are using trusted reverse proxy and not remember you manually overrided this value, please take time to check your config for optimal behavior.

### Details
[Fastify recommend not trusting X-Forwarded-For IPs](https://fastify.dev/docs/latest/Reference/Server/#trustproxy)
Due to misconfiguration in https://github.com/misskey-dev/misskey/blob/develop/packages/backend/src/server/api/SigninApiService.ts#L94 attacks can spoof their IPs.

### PoC

```
POST /api/signin-flow HTTP/1.1
Host: misskey.localhost:3123
Content-Length: 45
Content-Type: application/json
Connection: keep-alive
X-Forwarded-For: 127.1.1.31, 1.1.1.12

{"username":"admin",
	"password":"password"}
```
![image](https://github.com/user-attachments/assets/ce9f77e2-b339-4081-86a6-d44ed42e9ca5)


### Impact
An attacker can brute force accounts bypassing rate limiting protection.

## References
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-wwrj-3hvj-prpm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66482
- https://github.com/misskey-dev/misskey/commit/5512898463fa8487b9e6488912f35102b91f25f7
- https://github.com/misskey-dev/misskey
