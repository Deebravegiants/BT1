# [M] React Developer Tools extension Improper Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rxrc-rgv4-jpvx
CVE: CVE-2023-5654
CWE: CWE-116, CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-rxrc-rgv4-jpvx
Type: github-advisory

## Affected
- npm: `react-devtools-core` — affected >=0 <4.28.4

## Details
The React Developer Tools extension registers a message listener with window.addEventListener('message', <listener>) in a content script that is accessible to any webpage that is active in the browser. Within the listener is code that requests a URL derived from the received message via fetch(). The URL is not validated or sanitised before it is fetched, thus allowing a malicious web page to arbitrarily fetch URL’s via the victim's browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5654
- https://github.com/facebook/react/pull/27417
- https://github.com/facebook/react/commit/09285d5a7f1c08bec09f44cec3d0518a603597fc
- https://github.com/facebook/react/commit/94d5b5b2bf5204ebd289a113989c0e2c51b626ef
- https://gist.github.com/CalumHutton/1fb89b64409570a43f89d1fd3274b231
- https://github.com/facebook/react
