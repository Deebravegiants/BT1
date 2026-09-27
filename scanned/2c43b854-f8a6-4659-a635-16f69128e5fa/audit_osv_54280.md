# [M] CVE-2023-45920

## Summary
Severity: Medium
Advisory: CVE-2023-45920
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-45920
Type: osv

## Details
Xfig v3.2.8 was discovered to contain a NULL pointer dereference when calling XGetWMHints(). NOTE: this is disputed because it is not expected that an X application should continue to run when there is arbitrary anomalous behavior from the X server or window manager.

## References
- http://packetstormsecurity.com/files/176803/Xfig-3.2.8-Null-Pointer.html
- http://seclists.org/fulldisclosure/2024/Jan/48
- https://sourceforge.net/p/mcj/tickets/155/
