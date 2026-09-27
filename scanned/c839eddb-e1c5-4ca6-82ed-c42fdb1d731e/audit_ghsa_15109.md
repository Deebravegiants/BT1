# [C] Arbitrary remote code execution within `wrangler dev` Workers sandbox

## Summary
Severity: Critical
Advisory: GHSA-f8mp-x433-5wpf
CVE: CVE-2023-7080
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-f8mp-x433-5wpf
Type: github-advisory

## Affected
- npm: `wrangler` — affected >=3.0.0 <3.19.0
- npm: `wrangler` — affected >=2.0.0 <2.20.2

## Details
### Impact
The V8 inspector intentionally allows arbitrary code execution within the Workers sandbox for debugging. `wrangler dev` would previously start an inspector server listening on all network interfaces. This would allow an attacker on the local network to connect to the inspector and run arbitrary code. Additionally, the inspector server did not validate `Origin`/`Host` headers, granting an attacker that can trick any user on the local network into opening a malicious website the ability to run code. If `wrangler dev --remote` was being used, an attacker could access production resources if they were bound to the worker.

### Patches
This issue was fixed in `wrangler@3.19.0` and `wrangler@2.20.2`. Whilst `wrangler dev`'s inspector server listens on local interfaces by default as of `wrangler@3.16.0`, an [SSRF vulnerability in `miniflare`](https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-fwvg-2739-22v7) allowed access from the local network until `wrangler@3.18.0`. `wrangler@3.19.0` and `wrangler@2.20.2` introduced validation for the `Origin`/`Host` headers.

### Workarounds
Unfortunately, Wrangler doesn't provide any configuration for which host that inspector server should listen on. Please upgrade to at least `wrangler@3.16.0`, and configure Wrangler to listen on local interfaces instead with `wrangler dev --ip 127.0.0.1` to prevent SSRF. This removes the local network as an attack vector, but does not prevent an attack from visiting a malicious website.

### References
- https://github.com/cloudflare/workers-sdk/issues/4430
- https://github.com/cloudflare/workers-sdk/pull/4437
- https://github.com/cloudflare/workers-sdk/pull/4535
- https://github.com/cloudflare/workers-sdk/pull/4550

## References
- https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-f8mp-x433-5wpf
- https://nvd.nist.gov/vuln/detail/CVE-2023-7080
- https://github.com/cloudflare/workers-sdk/issues/4430
- https://github.com/cloudflare/workers-sdk/pull/4437
- https://github.com/cloudflare/workers-sdk/pull/4535
- https://github.com/cloudflare/workers-sdk/pull/4550
- https://github.com/cloudflare/workers-sdk/commit/05b1bbd2f5b8e60268e30c276067c3a3ae1239cf
- https://github.com/cloudflare/workers-sdk/commit/29df8e17545bf3926b6d61678b596be809d40c6d
- https://github.com/cloudflare/workers-sdk/commit/49a469601adaa9eb9e1f2d6de197c1979d5c6c1b
- https://github.com/cloudflare/workers-sdk/commit/63708a94fb7a055bf15fa963f2d598b47b11d3c0
- https://github.com/cloudflare/workers-sdk
