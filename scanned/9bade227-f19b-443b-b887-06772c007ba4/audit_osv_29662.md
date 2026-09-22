# [H] CVE-2024-45238

## Summary
Severity: High
Advisory: CVE-2024-45238
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-24
Source: https://osv.dev/vulnerability/CVE-2024-45238
Type: osv

## Details
An issue was discovered in Fort before 1.6.3. A malicious RPKI repository that descends from a (trusted) Trust Anchor can serve (via rsync or RRDP) a resource certificate containing a bit string that doesn't properly decode into a Subject Public Key. OpenSSL does not report this problem during parsing, and when compiled with OpenSSL libcrypto versions below 3, Fort recklessly dereferences the pointer. Because Fort is an RPKI Relying Party, a crash can lead to Route Origin Validation unavailability, which can lead to compromised routing.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00030.html
- https://nicmx.github.io/FORT-validator/CVE.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45238.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45238
