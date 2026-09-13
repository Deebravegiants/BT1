# [M] CVE-2026-10546

## Summary
Severity: Medium
Advisory: CVE-2026-10546
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-10546
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.9.3 contains a Server-Side Request Forgery (SSRF) vulnerability in the URL component ( src/lfx/src/lfx/components/data_source/url.py ) due to a Time-of-Check/Time-of-Use (TOCTOU) race condition that can be exploited via DNS rebinding.

## References
- https://www.ibm.com/support/pages/node/7277560
