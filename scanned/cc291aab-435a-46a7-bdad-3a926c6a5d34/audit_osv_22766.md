# [M] CVE-2022-3821

## Summary
Severity: Medium
Advisory: CVE-2022-3821
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-08
Source: https://osv.dev/vulnerability/CVE-2022-3821
Type: osv

## Details
An off-by-one Error issue was discovered in Systemd in format_timespan() function of time-util.c. An attacker could supply specific values for time and accuracy that leads to buffer overrun in format_timespan(), leading to a Denial of Service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3821.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RVBQC2VLSDVQAPJTEMTREXDL4HYLXG2P/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3821
- https://security.gentoo.org/glsa/202305-15
- https://bugzilla.redhat.com/show_bug.cgi?id=2139327
- https://github.com/systemd/systemd/issues/23928
- https://github.com/systemd/systemd/commit/9102c625a673a3246d7e73d8737f3494446bad4e
- https://github.com/systemd/systemd/pull/23933
- https://lists.debian.org/debian-lts-announce/2023/06/msg00036.html
