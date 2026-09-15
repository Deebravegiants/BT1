# [H] @sveltejs/kit has memory amplification DoS vulnerability in Remote Functions binary form deserializer (application/x-sveltekit-formdata)

## Summary
Severity: High
Advisory: GHSA-j2f3-wq62-6q46
CVE: CVE-2026-22803
CWE: CWE-789
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-j2f3-wq62-6q46
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=2.49.0 <2.49.5

## Details
## Summary

The experimental `form` remote function uses a binary data format containing a representation of submitted form data. A specially-crafted payload can cause the server to allocate a large amount of memory, causing DoS via memory exhaustion.

## Details

When a form is submitted to a remote function endpoint, the SvelteKit client encodes the data using a custom format, and POSTs it to the endpoint as a request with an `application/x-sveltekit-formdata` content type.

The first few bytes of the request body encode the length of the data. SvelteKit will attempt to read the request body up until the specified offset, but if the body is not yet available then an array buffer of that size will be created eagerly to accommodate it as it arrives.

An attacker can force this code path by sending a small payload that specifies a large data length, then stalling the connection. The resulting array buffer will be held in memory, potentially causing memory exhaustion.

## Impact

- Vulnerability type: Availability / memory exhaustion (memory amplification).
- Who is impacted: SvelteKit apps with `experimental.remoteFunctions` enabled, and that expose a reachable Remote Form endpoint.
- Attack: an unauthenticated attacker can repeatedly open connections, send only the 8-byte header/prefix (with large data_length), and stall the body to hold large allocations, exhausting memory.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-j2f3-wq62-6q46
- https://nvd.nist.gov/vuln/detail/CVE-2026-22803
- https://github.com/sveltejs/kit/commit/8ed8155215b9a74012fecffb942ad9a793b274e5
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/%40sveltejs%2Fkit%402.49.5
- https://github.com/sveltejs/kit/releases/tag/@sveltejs%2Fadapter-node@5.5.1
