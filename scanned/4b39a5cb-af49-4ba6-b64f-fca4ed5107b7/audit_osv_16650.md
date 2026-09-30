# [C] CVE-2019-8428

## Summary
Severity: Critical
Advisory: CVE-2019-8428
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/CVE-2019-8428
Type: osv

## Details
ZoneMinder before 1.32.3 has SQL Injection via the skins/classic/views/control.php groupSql parameter, as demonstrated by a newGroup[MonitorIds][] value.

## References
- https://github.com/LoRexxar/CVE_Request/tree/master/zoneminder%20vul%20before%20v1.32.3#skinsclassicviewscontrolphp-line-35-second-order-sqli
- https://www.seebug.org/vuldb/ssvid-97765
