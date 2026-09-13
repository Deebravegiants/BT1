# [M] Ipa: freeipa: authenticated dos in `otptoken-add` via unbounded otp key decoding/re-encoding

## Summary
Severity: Medium
Advisory: CVE-2026-73196
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-73196
Type: osv

## Details
A flaw was found in FreeIPA. A low-privilege authenticated user can exploit this vulnerability by submitting an oversized One-Time Password (OTP) key value. This oversized key is then decoded and re-encoded without proper size limits, consuming excessive CPU and memory resources. This can lead to a denial of service, degrading the availability of the IPA service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-73196
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73196.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73196
- https://bugzilla.redhat.com/show_bug.cgi?id=2474712
