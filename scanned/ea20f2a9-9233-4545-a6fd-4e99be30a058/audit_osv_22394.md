# [H] CVE-2022-28391

## Summary
Severity: High
Advisory: CVE-2022-28391
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-03
Source: https://osv.dev/vulnerability/CVE-2022-28391
Type: osv

## Details
BusyBox through 1.35.0 allows remote attackers to execute arbitrary code if netstat is used to print a DNS PTR record's value to a VT compatible terminal. Alternatively, the attacker could choose to change the terminal's colors.

## References
- https://git.alpinelinux.org/aports/plain/main/busybox/0001-libbb-sockaddr2str-ensure-only-printable-characters-.patch
- https://git.alpinelinux.org/aports/plain/main/busybox/0002-nslookup-sanitize-all-printed-strings-with-printable.patch
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/28xxx/CVE-2022-28391.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-28391
- https://gitlab.alpinelinux.org/alpine/aports/-/issues/13661
