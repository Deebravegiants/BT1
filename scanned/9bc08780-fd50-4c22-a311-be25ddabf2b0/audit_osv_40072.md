# [M] Valhalla has reflected XSS via unsanitized JSONP callback parameter

## Summary
Severity: Medium
Advisory: CVE-2026-49294
Aliases: GHSA-85xx-39j8-r56x
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-49294
Type: osv

## Details
Valhalla is an open source routing engine and accompanying libraries for use with OpenStreetMap data. Versions 3.6.3 and prior are vulnerable to reflected cross-site scripting (XSS) due to improper neutralization of input in the JSONP callback parameter. When a request specifies a JSONP callback, the value is reflected directly into the HTTP response body with Content-Type: application/javascript, without any validation, output encoding, or allowlist filtering. An attacker can craft a URL containing arbitrary JavaScript in the callback parameter; if a victim is induced to load that URL via a <script src="..."> tag, the injected script executes in the context of the serving origin, potentially leading to session token theft, credential disclosure, or actions performed on behalf of the victim. This issue was not fixed at time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49294.json
- https://github.com/valhalla/valhalla/security/advisories/GHSA-85xx-39j8-r56x
- https://nvd.nist.gov/vuln/detail/CVE-2026-49294
