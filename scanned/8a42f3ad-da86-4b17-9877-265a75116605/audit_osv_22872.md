# [M] CVE-2022-39836

## Summary
Severity: Medium
Advisory: CVE-2022-39836
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-24
Source: https://osv.dev/vulnerability/CVE-2022-39836
Type: osv

## Details
An issue was discovered in Connected Vehicle Systems Alliance (COVESA) dlt-daemon through 2.18.8. Due to a faulty DLT file parser, a crafted DLT file that crashes the process can be created. This is due to missing validation checks. There is a heap-based buffer over-read of one byte.

## References
- https://seclists.org/fulldisclosure/2022/Sep/24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39836.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-39836
- https://sec-consult.com/vulnerability-lab/advisory/multiple-memory-corruption-vulnerabilities-in-covesa-dlt-daemon/
- https://lists.debian.org/debian-lts-announce/2024/06/msg00021.html
