# [H] Livewire Filemanager does not restrict uploaded file types

## Summary
Severity: High
Advisory: GHSA-9g95-48c6-r778
CVE: CVE-2025-14894
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-9g95-48c6-r778
Type: github-advisory

## Affected
- Packagist: `livewire-filemanager/filemanager` — affected >=0

## Details
Livewire Filemanager, commonly used in Laravel applications, contains LivewireFilemanagerComponent.php, which does not perform file type and MIME validation, allowing for RCE through upload of a malicious php file that can then be executed via the /storage/ URL if a commonly performed setup process within Laravel applications has been completed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14894
- https://github.com/livewire-filemanager/filemanager
- https://github.com/livewire-filemanager/filemanager/blob/master/docs.md#security
- https://hackingbydoing.wixsite.com/hackingbydoing/post/unauthenticated-rce-in-livewire-filemanager
- https://www.kb.cert.org/vuls/id/650657
