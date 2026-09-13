# [H] CVE-2023-26604

## Summary
Severity: High
Advisory: CVE-2023-26604
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-03
Source: https://osv.dev/vulnerability/CVE-2023-26604
Type: osv

## Details
systemd before 247 does not adequately block local privilege escalation for some Sudo configurations, e.g., plausible sudoers files in which the "systemctl status" command may be executed. Specifically, systemd does not set LESSSECURE to 1, and thus other programs may be launched from the less program. This presents a substantial security risk when running systemctl from Sudo, because less executes as root when the terminal size is too small to show the complete systemctl output.

## References
- http://packetstormsecurity.com/files/174130/systemd-246-Local-Root-Privilege-Escalation.html
- https://github.com/systemd/systemd/blob/main/NEWS#L4335-L4340
- https://medium.com/%40zenmoviefornotification/saidov-maxim-cve-2023-26604-c1232a526ba7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26604.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26604
- https://security.netapp.com/advisory/ntap-20230505-0009/
- https://blog.compass-security.com/2012/10/dangerous-sudoers-entries-part-2-insecure-functionality/
- https://lists.debian.org/debian-lts-announce/2023/03/msg00032.html
