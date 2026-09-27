# [H] Libjpeg-turbo all version have a stack-based buffer overflow in the "transform" component

## Summary
Severity: High
Advisory: JLSEC-2025-179
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-179
Type: osv

## Affected
- Julia: `JpegTurbo_jll` — affected >=0 <2.1.0+0

## Details
Libjpeg-turbo all version have a stack-based buffer overflow in the "transform" component. A remote attacker can send a malformed jpeg file to the service and cause arbitrary code execution or denial of service of the target service.

## References
- https://cwe.mitre.org/data/definitions/121.html
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/392
