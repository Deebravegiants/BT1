# [M] CVE-2024-42328

## Summary
Severity: Medium
Advisory: CVE-2024-42328
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-42328
Type: osv

## Details
When the webdriver for the Browser object downloads data from a HTTP server, the data pointer is set to NULL and is allocated only in curl_write_cb when receiving data. If the server's response is an empty document, then wd->data in the code below will remain NULL and an attempt to read from it will result in a crash.

## References
- https://support.zabbix.com/browse/ZBX-25624
