# [M] Qwik SSR XSS via Unsafe Virtual Node Serialization

## Summary
Severity: Medium
Advisory: GHSA-m6jq-g7gq-5w3c
CVE: CVE-2026-25148
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-m6jq-g7gq-5w3c
Type: github-advisory

## Affected
- npm: `@builder.io/qwik-city` — affected >=0 <1.19.0

## Details
### Summary

**Description**
A Cross-site Scripting (CWE-79) vulnerability in Qwik.js' server-side rendering virtual attribute serialization allows a remote attacker to inject arbitrary web scripts into server-rendered pages via virtual attributes. Successful exploitation permits script execution in a victim's browser in the context of the affected origin. This affects qwik-city before version 1.19.0. This has been patched in qwik-city version 1.19.0.

### Impact
This vulnerability impacts applications that dynamically populate Virtual Node attributes with keys/values that users can influence. Applications that hard-code these keys/values are unaffected.

Qwik doesn't use traditional hydration. Instead, it serializes application state into the HTML so the client can resume execution from the server-rendered output. To support this, Qwik v1 marks component boundaries with HTML comments. SSR builds comment content for Virtual components by concatenating structural attribute names and values without any escaping or quoting. An attacker-controlled key or value can prematurely close the HTML comment and inject arbitrary HTML/JS.

Successful exploitation permits script execution in a victim’s browser in the context of the affected origin. Additionally, because Qwik uses these serialized comment markers for resumability, breaking comment structure can lead to resume/hydration desync and unexpected client-side behavior.

### Patches
This has been patched in qwik-city version 1.19.0. Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-m6jq-g7gq-5w3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-25148
- https://github.com/QwikDev/qwik/commit/fe2d9232c0bcec99411d51a00dae29295871d094
- https://github.com/QwikDev/qwik
