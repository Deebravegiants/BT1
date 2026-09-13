# [M] CVE-2015-7851

## Summary
Severity: Medium
Advisory: CVE-2015-7851
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2015-7851
Type: osv

## Details
Directory traversal vulnerability in the save_config function in ntpd in ntp_control.c in NTP before 4.2.8p4, when used on systems that do not use '\' or '/' characters for directory separation such as OpenVMS, allows remote authenticated users to overwrite arbitrary files.

## References
- http://support.ntp.org/bin/view/Main/NtpBug2918
- http://support.ntp.org/bin/view/Main/SecurityNotice
- http://www.talosintel.com/reports/TALOS-2015-0062/
- http://www.talosintel.com/reports/TALOS-2015-0062/
