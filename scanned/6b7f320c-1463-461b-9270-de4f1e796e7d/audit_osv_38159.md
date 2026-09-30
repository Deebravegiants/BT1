# [M] whisperX REST API: SSRF in download_from_url() — URL validation happens after HTTP request, extension bypass via .mp3

## Summary
Severity: Medium
Advisory: CVE-2026-34981
Aliases: GHSA-6rc7-r867-c635
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-34981
Type: osv

## Details
The whisperX API is a tool for enhancing and analyzing audio content. From 0.3.1 to 0.5.0, FileService.download_from_url() in app/services/file_service.py calls requests.get(url) with zero URL validation. The file extension check occurs AFTER the HTTP request is already made, and can be bypassed by appending .mp3 to any internal URL. The /speech-to-text-url endpoint is unauthenticated. This vulnerability is fixed in 0.6.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34981.json
- https://github.com/pavelzbornik/whisperX-FastAPI/security/advisories/GHSA-6rc7-r867-c635
- https://nvd.nist.gov/vuln/detail/CVE-2026-34981
- https://github.com/pavelzbornik/whisperX-FastAPI/issues/256
- https://github.com/pavelzbornik/whisperX-FastAPI/commit/ef78fe2001deede5354031e4200d41c6a7e8cbfc
