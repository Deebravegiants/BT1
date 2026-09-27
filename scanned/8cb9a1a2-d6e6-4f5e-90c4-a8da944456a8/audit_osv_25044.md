# [H] CVE-2023-30082

## Summary
Severity: High
Advisory: CVE-2023-30082
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-14
Source: https://osv.dev/vulnerability/CVE-2023-30082
Type: osv

## Details
A denial of service attack might be launched against the server if an unusually lengthy password (more than 10000000 characters) is supplied using the osTicket application. This can cause the website to go down or stop responding. When a long password is entered, this procedure will consume all available CPU and memory.

## References
- https://github.com/manavparekh/CVEs/blob/main/CVE-2023-30082/Steps%20to%20reproduce.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30082.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30082
- https://blog.manavparekh.com/2023/06/cve-2023-30082.html
