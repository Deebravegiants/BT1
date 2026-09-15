# [H] CVE-2021-40402

## Summary
Severity: High
Advisory: CVE-2021-40402
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2021-40402
Type: osv

## Details
An out-of-bounds read vulnerability exists in the RS-274X aperture macro multiple outline primitives functionality of Gerbv 2.7.0 and dev (commit b5f1eacd), and Gerbv forked 2.7.1 and 2.8.0. A specially-crafted Gerber file can lead to information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1416
