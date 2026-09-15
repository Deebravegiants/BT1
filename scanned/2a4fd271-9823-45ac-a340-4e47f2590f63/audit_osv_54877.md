# [H] CVE-2024-55581

## Summary
Severity: High
Advisory: CVE-2024-55581
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2024-55581
Type: osv

## Details
When AdaCore Ada Web Server 25.0.0 is linked with GnuTLS, the default behaviour of AWS.Client is vulnerable to a man-in-the-middle attack because of lack of verification of an HTTPS server's certificate (unless the using program specifies a TLS configuration).

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00007.html
- https://docs.adacore.com/corp/security-advisories/SEC.AWS-0056-v1.pdf
