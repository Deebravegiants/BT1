# [H] CVE-2021-40400

## Summary
Severity: High
Advisory: CVE-2021-40400
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2021-40400
Type: osv

## Details
An out-of-bounds read vulnerability exists in the RS-274X aperture macro outline primitive functionality of Gerbv 2.7.0 and dev (commit b5f1eacd) and the forked version of Gerbv (commit d7f42a9a). A specially-crafted Gerber file can lead to information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1413
