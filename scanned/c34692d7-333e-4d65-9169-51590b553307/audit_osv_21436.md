# [H] CVE-2021-43045

## Summary
Severity: High
Advisory: CVE-2021-43045
Aliases: GHSA-868x-rg4c-cjqg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-06
Source: https://osv.dev/vulnerability/CVE-2021-43045
Type: osv

## Details
A vulnerability in the .NET SDK of Apache Avro allows an attacker to allocate excessive resources, potentially causing a denial-of-service attack. This issue affects .NET applications using Apache Avro version 1.10.2 and prior versions. Users should update to version 1.11.0 which addresses this issue.

## References
- http://www.openwall.com/lists/oss-security/2022/01/06/8
- https://lists.apache.org/thread/5fttw9vk6gd2p3b846nox7hcj5469xfd
