# [H] CVE-2021-40401

## Summary
Severity: High
Advisory: CVE-2021-40401
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2021-40401
Type: osv

## Details
A use-after-free vulnerability exists in the RS-274X aperture definition tokenization functionality of Gerbv 2.7.0 and dev (commit b5f1eacd) and Gerbv forked 2.7.1. A specially-crafted gerber file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TUM5GIUZJ7AVHVCXDZW6ZVCAPV2ISN47/
- https://www.debian.org/security/2022/dsa-5306
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1415
