# [M] CVE-2019-8337

## Summary
Severity: Medium
Advisory: CVE-2019-8337
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-02-13
Source: https://osv.dev/vulnerability/CVE-2019-8337
Type: osv

## Details
In msmtp 1.8.2 and mpop 1.4.3, when tls_trust_file has its default configuration, certificate-verification results are not properly checked.

## References
- https://gitlab.marlam.de/marlam/mpop/commit/b51a6c6b8b83bf0913cc52fa2ff64307e987a5b8
- https://marlam.de/mpop/news/mpop-1-4-3/
- https://marlam.de/msmtp/news/
