# [M] CVE-2018-25262

## Summary
Severity: Medium
Advisory: CVE-2018-25262
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2018-25262
Type: osv

## Details
Angry IP Scanner for Linux 3.5.3 contains a denial of service vulnerability that allows local attackers to crash the application by supplying malformed input to the port selection field. Attackers can craft a malicious string containing buffer overflow patterns and paste it into the Preferences Ports tab to trigger an application crash.

## References
- https://angryip.org/
- https://www.vulncheck.com/advisories/angry-ip-scanner-for-linux-denial-of-service
- https://www.exploit-db.com/exploits/46038
