# [C] CVE-2019-20478

## Summary
Severity: Critical
Advisory: CVE-2019-20478
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-19
Source: https://osv.dev/vulnerability/CVE-2019-20478
Type: osv

## Details
In ruamel.yaml through 0.16.7, the load method allows remote code execution if the application calls this method with an untrusted argument. In other words, this issue affects developers who are unaware of the need to use methods such as safe_load in these use cases.

## References
- https://www.exploit-db.com/exploits/47655
