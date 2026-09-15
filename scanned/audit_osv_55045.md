# [C] CVE-2024-9680

## Summary
Severity: Critical
Advisory: CVE-2024-9680
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-9680
Type: osv

## Details
An attacker was able to achieve code execution in the content process by exploiting a use-after-free in Animation timelines. We have had reports of this vulnerability being exploited in the wild. This vulnerability affects Firefox < 131.0.2, Firefox ESR < 128.3.1, Firefox ESR < 115.16.1, Thunderbird < 131.0.1, Thunderbird < 128.3.1, and Thunderbird < 115.16.0.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-9680
- https://www.mozilla.org/security/advisories/mfsa2024-51/
- https://www.mozilla.org/security/advisories/mfsa2024-52/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1923344
- https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=281992
- https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2024-49039
- https://lists.debian.org/debian-lts-announce/2024/10/msg00005.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00006.html
