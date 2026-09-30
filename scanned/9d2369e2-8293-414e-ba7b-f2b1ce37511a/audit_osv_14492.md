# [C] CVE-2019-10053

## Summary
Severity: Critical
Advisory: CVE-2019-10053
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-13
Source: https://osv.dev/vulnerability/CVE-2019-10053
Type: osv

## Details
An issue was discovered in Suricata 4.1.x before 4.1.4. If the input of the function SSHParseBanner is composed only of a \n character, then the program runs into a heap-based buffer over-read. This occurs because the erroneous search for \r results in an integer underflow.

## References
- https://lists.openinfosecfoundation.org/pipermail/oisf-announce/
- https://suricata-ids.org/2019/04/30/suricata-4-1-4-released/
