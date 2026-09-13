# [H] CVE-2022-38725

## Summary
Severity: High
Advisory: CVE-2022-38725
Aliases: GHSA-7932-4fc6-pvmc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-23
Source: https://osv.dev/vulnerability/CVE-2022-38725
Type: osv

## Details
An integer overflow in the RFC3164 parser in One Identity syslog-ng 3.0 through 3.37 allows remote attackers to cause a Denial of Service via crafted syslog input that is mishandled by the tcp or network function. syslog-ng Premium Edition 7.0.30 and syslog-ng Store Box 6.10.0 are also affected.

## References
- https://lists.balabit.hu/pipermail/syslog-ng/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/38xxx/CVE-2022-38725.json
- https://github.com/syslog-ng/syslog-ng/security/advisories/GHSA-7932-4fc6-pvmc
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J3TZ7U2GQTAHVHJXSSEHQS5D2Q5T6SZB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QU36HCM3VZYANUYFC6XFYEYJEKQPA2Q7/
- https://nvd.nist.gov/vuln/detail/CVE-2022-38725
- https://security.gentoo.org/glsa/202305-09
- https://www.debian.org/security/2023/dsa-5369
- https://lists.debian.org/debian-lts-announce/2023/02/msg00043.html
