# [M] CVE-2019-11778

## Summary
Severity: Medium
Advisory: CVE-2019-11778
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2019-09-18
Source: https://osv.dev/vulnerability/CVE-2019-11778
Type: osv

## Details
If an MQTT v5 client connects to Eclipse Mosquitto versions 1.6.0 to 1.6.4 inclusive, sets a last will and testament, sets a will delay interval, sets a session expiry interval, and the will delay interval is set longer than the session expiry interval, then a use after free error occurs, which has the potential to cause a crash in some situations.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=551162
