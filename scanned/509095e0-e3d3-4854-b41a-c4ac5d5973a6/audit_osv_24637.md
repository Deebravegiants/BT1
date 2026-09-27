# [H] CVE-2023-24472

## Summary
Severity: High
Advisory: CVE-2023-24472
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-24472
Type: osv

## Details
A denial of service vulnerability exists in the FitsOutput::close() functionality of OpenImageIO Project OpenImageIO v2.4.7.1. A specially crafted ImageOutput Object can lead to denial of service. An attacker can provide malicious input to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00005.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1709
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1709
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24472.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24472
