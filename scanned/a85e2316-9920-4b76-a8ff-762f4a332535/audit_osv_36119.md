# [H] Emlog vulnerable to Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: CVE-2026-21433
Aliases: GHSA-6rwr-c8hc-mjj4
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-01-02
Source: https://osv.dev/vulnerability/CVE-2026-21433
Type: osv

## Details
Emlog is an open source website building system. Versions up to and including 2.5.19 are vulnerable to server-side Out-of-Band (OOB) requests / SSRF via uploaded SVG files. An attacker can upload a crafted SVG to http[:]//emblog/admin/media[.]php which contains external resource references. When the server processes/renders the SVG (thumbnailing, preview, or sanitization), it issues an HTTP request to the attacker-controlled host. Impact: server-side SSRF/OOB leading to internal network probing and potential metadata/credential exposure. As of time of publication, no known patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21433.json
- https://github.com/emlog/emlog/security/advisories/GHSA-6rwr-c8hc-mjj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-21433
