# [H] CVE-2020-17541

## Summary
Severity: High
Advisory: CVE-2020-17541
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2020-17541
Type: osv

## Details
Libjpeg-turbo all version have a stack-based buffer overflow in the "transform" component. A remote attacker can send a malformed jpeg file to the service and cause arbitrary code execution or denial of service of the target service.

## References
- https://cwe.mitre.org/data/definitions/121.html
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/392
