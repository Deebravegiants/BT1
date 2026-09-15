# [M] CVE-2023-31207

## Summary
Severity: Medium
Advisory: CVE-2023-31207
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-02
Source: https://osv.dev/vulnerability/CVE-2023-31207
Type: osv

## Details
Transmission of credentials within query parameters in Checkmk <= 2.1.0p26, <= 2.0.0p35, and <= 2.2.0b6 (beta) may cause the automation user's secret to be written to the site Apache access log.

## References
- https://checkmk.com/werk/15189
