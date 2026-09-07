# [H] Anki's local HTTP server does not sufficiently validate requests

## Summary
Severity: High
Advisory: GHSA-869j-r97x-hx2g
CVE: CVE-2026-59153
CWE: CWE-22, CWE-346
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-869j-r97x-hx2g
Type: github-advisory

## Affected
- PyPI: `aqt` — affected >=0 <25.9.3

## Details
## Summary

Anki launches a local HTTP server to serve media files and web pages for parts of its interface. While the server has a CORS setup, requests from other origins were not blocked, allowing malicious websites to potentially trigger side-effecting requests.

## Browser impact

The severity varies by browser because of Private Network Access (PNA), a newer spec that restricts web pages from making requests to localhost/local network addresses:

Chrome/Chromium (including Edge, Brave): Largely protected, as Chrome has implemented PNA restrictions for several years and now puts local network access behind a permission prompt.
Safari: Hasn't implemented PNA yet, though macOS has some OS-level protections.
Firefox: Most vulnerable — hasn't implemented PNA yet, though it's reportedly planned for Firefox 151.

## Patches

The issue was fixed as of Anki 25.09.3

### References

https://x.com/taviso/status/2051310678800253318

## References
- https://github.com/ankitects/anki/security/advisories/GHSA-869j-r97x-hx2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-59153
- https://github.com/ankitects/anki/commit/858e5689d0e4fd24f74856c7e8f245412694a219
- https://github.com/ankitects/anki
- https://github.com/ankitects/anki/releases/tag/25.09.3
- https://x.com/taviso/status/2051310678800253318
