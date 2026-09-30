# [H] RCE in Cruddiy

## Summary
Severity: High
Advisory: CVE-2024-4748
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-4748
Type: osv

## Details
The CRUDDIY project is vulnerable to shell command injection via sending a crafted POST request to the application server. 
The exploitation risk is limited since CRUDDIY is meant to be launched locally. Nevertheless, a user with the project running on their computer might visit a website which would send such a malicious request to the locally launched server.

## References
- https://cert.pl/en/posts/2024/06/CVE-2024-4748
- https://cert.pl/posts/2024/06/CVE-2024-4748
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4748.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4748
- https://github.com/jan-vandenberg/cruddiy/issues/67
- https://github.com/jan-vandenberg/cruddiy
