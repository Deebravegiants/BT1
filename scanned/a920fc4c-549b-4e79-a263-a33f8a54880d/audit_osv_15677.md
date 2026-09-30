# [C] CVE-2019-18662

## Summary
Severity: Critical
Advisory: CVE-2019-18662
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-02
Source: https://osv.dev/vulnerability/CVE-2019-18662
Type: osv

## Details
An issue was discovered in YouPHPTube through 7.7. User input passed through the live_stream_code POST parameter to /plugin/LiveChat/getChat.json.php is not properly sanitized (in getFromChat in plugin/LiveChat/Objects/LiveChatObj.php) before being used to construct a SQL query. This can be exploited by malicious users to, e.g., read sensitive data from the database through in-band SQL Injection attacks. Successful exploitation of this vulnerability requires the Live Chat plugin to be enabled.

## References
- http://packetstormsecurity.com/files/155564/YouPHPTube-7.7-SQL-Injection.html
- http://seclists.org/fulldisclosure/2019/Dec/9
- https://github.com/YouPHPTube/YouPHPTube/issues/2202
