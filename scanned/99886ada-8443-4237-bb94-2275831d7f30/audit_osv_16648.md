# [C] CVE-2019-8423

## Summary
Severity: Critical
Advisory: CVE-2019-8423
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/CVE-2019-8423
Type: osv

## Details
ZoneMinder through 1.32.3 has SQL Injection via the skins/classic/views/events.php filter[Query][terms][0][cnj] parameter.

## References
- https://github.com/LoRexxar/CVE_Request/tree/master/zoneminder%20vul%20before%20v1.32.3#skinsclassicviewseventsphp-line-44-sql-injection
- https://www.seebug.org/vuldb/ssvid-97761
