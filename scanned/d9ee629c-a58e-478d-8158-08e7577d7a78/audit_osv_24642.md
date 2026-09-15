# [M] CVE-2023-24604

## Summary
Severity: Medium
Advisory: CVE-2023-24604
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-05-29
Source: https://osv.dev/vulnerability/CVE-2023-24604
Type: osv

## Details
OX App Suite before backend 7.10.6-rev37 does not check HTTP header lengths when downloading, e.g., potentially allowing a crafted iCal feed to provide an unlimited amount of header data.

## References
- http://seclists.org/fulldisclosure/2023/May/3
- https://open-xchange.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24604.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24604
