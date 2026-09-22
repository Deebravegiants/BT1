# [M] CVE-2018-18837

## Summary
Severity: Medium
Advisory: CVE-2018-18837
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2018-18837
Type: osv

## Details
An issue was discovered in Netdata 1.10.0. HTTP Header Injection exists via the api/v1/data filename parameter because of web_client_api_request_v1_data in web/api/web_api_v1.c.

## References
- https://github.com/netdata/netdata/blob/798c141c49ee85bddc8f48f25d2cb593ec96da07/web/api/web_api_v1.c#L367-L370
- https://github.com/netdata/netdata/pull/4521
- https://github.com/netdata/netdata/commit/92327c9ec211bd1616315abcb255861b130b97ca
- https://www.red4sec.com/cve/netdata_header_injection.txt
