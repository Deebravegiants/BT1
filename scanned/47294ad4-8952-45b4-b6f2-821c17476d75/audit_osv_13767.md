# [M] CVE-2018-25266

## Summary
Severity: Medium
Advisory: CVE-2018-25266
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2018-25266
Type: osv

## Details
Angry IP Scanner 3.5.3 contains a buffer overflow vulnerability in the preferences dialog that allows local attackers to crash the application by supplying an excessively large string. Attackers can generate a file containing a massive buffer of repeated characters and paste it into the unavailable value field in the display preferences to trigger a denial of service.

## References
- https://angryip.org
- https://www.vulncheck.com/advisories/angry-ip-scanner-denial-of-service-via-preferences-buffer-overflow
- https://www.exploit-db.com/exploits/45993
