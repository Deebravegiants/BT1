# [C] CVE-2016-6813

## Summary
Severity: Critical
Advisory: CVE-2016-6813
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2016-6813
Type: osv

## Details
Apache CloudStack 4.1 to 4.8.1.0 and 4.9.0.0 contain an API call designed to allow a user to register for the developer API. If a malicious user is able to determine the ID of another (non-"root") CloudStack user, the malicious user may be able to reset the API keys for the other user, in turn accessing their account and resources.

## References
- http://mail-archives.apache.org/mod_mbox/www-announce/201610.mbox/%3CCAJtfqCupOYQoNY2BNx86_zauses_MpmpiX8WciO_DEaWp6uNig%40mail.gmail.com%3E
- http://www.securityfocus.com/bid/93945
- https://s.apache.org/qV5l
