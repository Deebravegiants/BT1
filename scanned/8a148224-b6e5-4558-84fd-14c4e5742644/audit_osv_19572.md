# [H] CVE-2021-22150

## Summary
Severity: High
Advisory: CVE-2021-22150
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-22
Source: https://osv.dev/vulnerability/CVE-2021-22150
Type: osv

## Details
It was discovered that a user with Fleet admin permissions could upload a malicious package. Due to using an older version of the js-yaml library, this package would be loaded in an insecure manner, allowing an attacker to execute commands on the Kibana server.

## References
- https://discuss.elastic.co/t/elastic-stack-7-14-1-security-update/283077
- https://www.elastic.co/community/security
