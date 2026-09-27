# [H] CVE-2024-45239

## Summary
Severity: High
Advisory: CVE-2024-45239
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-24
Source: https://osv.dev/vulnerability/CVE-2024-45239
Type: osv

## Details
An issue was discovered in Fort before 1.6.3. A malicious RPKI repository that descends from a (trusted) Trust Anchor can serve (via rsync or RRDP) an ROA or a Manifest containing a null eContent field. Fort dereferences the pointer without sanitizing it first. Because Fort is an RPKI Relying Party, a crash can lead to Route Origin Validation unavailability, which can lead to compromised routing.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00030.html
- https://nicmx.github.io/FORT-validator/CVE.html
