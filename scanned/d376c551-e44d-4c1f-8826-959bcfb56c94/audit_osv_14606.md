# [H] CVE-2019-10244

## Summary
Severity: High
Advisory: CVE-2019-10244
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-10244
Type: osv

## Details
In Eclipse Kura versions up to 4.0.0, the Web UI package and component services, the Artemis simple Mqtt component and the emulator position service (not part of the device distribution) could potentially be target of XXE attack due to an improper factory and parser initialisation.

## References
- http://www.securityfocus.com/bid/107844
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=545835
