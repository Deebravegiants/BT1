# [H] The trudesk application allows large characters to insert in the input field "Full Name" on the signup field which can allow attackers to cause a Denial of Service (DoS) via a crafted HTTP request in polonel/trudesk

## Summary
Severity: High
Advisory: CVE-2022-1718
CVSS: 7.2 (CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-05-16
Source: https://osv.dev/vulnerability/CVE-2022-1718
Type: osv

## Details
The trudesk application allows large characters to insert in the input field "Full Name" on the signup field which can allow attackers to cause a Denial of Service (DoS) via a crafted HTTP request in GitHub repository polonel/trudesk prior to 1.2.2. This can lead to Denial of service.

## References
- https://huntr.dev/bounties/1ff8afe4-6ff7-45aa-a652-d8aac7e5be7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1718.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1718
- https://github.com/polonel/trudesk/commit/87e231e04495fb705fe1e03cb56fc4136bafe895
