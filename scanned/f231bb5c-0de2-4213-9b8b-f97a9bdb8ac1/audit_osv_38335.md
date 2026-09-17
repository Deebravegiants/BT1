# [M] CVE-2026-38979

## Summary
Severity: Medium
Advisory: CVE-2026-38979
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-38979
Type: osv

## Details
ajenti through v2.2.13 has a clickjacking weakness in the browser-facing login and administrative UI. In ajenti-core/aj/http.py, the core HTTP response path initializes an empty header list, forwards handler-added headers verbatim, and finalizes responses through WSGI start_response() without adding anti-framing protections such as X-Frame-Options or a Content-Security-Policy frame-ancestors restriction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38979.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38979
- https://github.com/ajenti/ajenti/commit/e54e83888fc7cb10061a18b04c1a7e3100d77f03
- https://github.com/ajenti/ajenti
