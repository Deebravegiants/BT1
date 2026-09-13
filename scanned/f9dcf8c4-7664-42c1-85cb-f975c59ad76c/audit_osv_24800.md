# [H] CVE-2023-26855

## Summary
Severity: High
Advisory: CVE-2023-26855
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2023-26855
Type: osv

## Details
The hashing algorithm of ChurchCRM v4.5.3 utilizes a non-random salt value which allows attackers to use precomputed hash tables or dictionary attacks to crack the hashed passwords.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26855.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26855
- https://github.com/ChurchCRM/CRM/issues/6449
