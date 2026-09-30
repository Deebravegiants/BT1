# [H] CVE-2020-15879

## Summary
Severity: High
Advisory: CVE-2020-15879
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-07-21
Source: https://osv.dev/vulnerability/CVE-2020-15879
Type: osv

## Details
Bitwarden Server 1.35.1 allows SSRF because it does not consider certain IPv6 addresses (ones beginning with fc, fd, fe, or ff, and the :: address) and certain IPv4 addresses (0.0.0.0/8, 127.0.0.0/8, and 169.254.0.0/16).

## References
- https://github.com/bitwarden/server/pull/827
