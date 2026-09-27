# [M] CVE-2018-18836

## Summary
Severity: Medium
Advisory: CVE-2018-18836
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2018-18836
Type: osv

## Details
An issue was discovered in Netdata 1.10.0. JSON injection exists via the api/v1/data tqx parameter because of web_client_api_request_v1_data in web/api/web_api_v1.c.

## References
- https://github.com/netdata/netdata/pull/4521
- https://www.red4sec.com/cve/netdata_json_injection.txt
- https://github.com/netdata/netdata/commit/92327c9ec211bd1616315abcb255861b130b97ca
- https://github.com/netdata/netdata/blob/798c141c49ee85bddc8f48f25d2cb593ec96da07/web/api/web_api_v1.c#L388
- https://github.com/netdata/netdata/blob/798c141c49ee85bddc8f48f25d2cb593ec96da07/web/api/web_api_v1.c#L403
