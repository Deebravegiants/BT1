# [M] CVE-2021-22139

## Summary
Severity: Medium
Advisory: CVE-2021-22139
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-22139
Type: osv

## Details
Kibana versions before 7.12.1 contain a denial of service vulnerability was found in the webhook actions due to a lack of timeout or a limit on the request size. An attacker with permissions to create webhook actions could drain the Kibana host connection pool, making Kibana unavailable for all other users.

## References
- https://discuss.elastic.co/t/7-12-1-security-update/271433
