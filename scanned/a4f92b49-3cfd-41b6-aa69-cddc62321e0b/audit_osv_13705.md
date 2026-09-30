# [H] CVE-2018-21035

## Summary
Severity: High
Advisory: CVE-2018-21035
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-28
Source: https://osv.dev/vulnerability/CVE-2018-21035
Type: osv

## Details
In Qt through 5.14.1, the WebSocket implementation accepts up to 2GB for frames and 2GB for messages. Smaller limits cannot be configured. This makes it easier for attackers to cause a denial of service (memory consumption).

## References
- https://codereview.qt-project.org/c/qt/qtwebsockets/+/284735
- https://bugreports.qt.io/browse/QTBUG-70693
