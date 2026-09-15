# [H] CVE-2020-14940

## Summary
Severity: High
Advisory: CVE-2020-14940
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-23
Source: https://osv.dev/vulnerability/CVE-2020-14940
Type: osv

## Details
An issue was discovered in io/gpx/GPXDocumentReader.java in TuxGuitar 1.5.4. It uses misconfigured XML parsers, leading to XXE while loading GP6 (.gpx) and GP7 (.gp) tablature files.

## References
- https://logicaltrust.net/blog/2020/06/tuxguitar.html
- https://sourceforge.net/p/tuxguitar/bugs/126/
