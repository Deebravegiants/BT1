# [C] CVE-2026-18749

## Summary
Severity: Critical
Advisory: CVE-2026-18749
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-18749
Type: osv

## Details
The type=track branch authorises on _is_my_case(t_attach.case) only and never checks VinceTrackAttachment.shared. A coordinator-uploaded case artefact that has NOT been marked shared is still retrievable by any case member who has (or is sent) its uuid — leaks not-yet-released coordinator material to vendors on the case.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18749.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18749
- https://github.com/CERTCC/VINCE/pull/235
- https://github.com/CERTCC/VINCE
