# [H] CVE-2017-12976

## Summary
Severity: High
Advisory: CVE-2017-12976
Aliases: HSEC-2023-0009
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-20
Source: https://osv.dev/vulnerability/CVE-2017-12976
Type: osv

## Details
git-annex before 6.20170818 allows remote attackers to execute arbitrary commands via an ssh URL with an initial dash character in the hostname, as demonstrated by an ssh://-eProxyCommand= URL, a related issue to CVE-2017-9800, CVE-2017-12836, CVE-2017-1000116, and CVE-2017-1000117.

## References
- http://source.git-annex.branchable.com/?p=source.git%3Ba=commit%3Bh=c24d0f0e8984576654e2be149005bc884fe0403a
- http://source.git-annex.branchable.com/?p=source.git%3Ba=commit%3Bh=df11e54788b254efebb4898b474de11ae8d3b471
- https://lists.debian.org/debian-lts-announce/2018/09/msg00004.html
- http://source.git-annex.branchable.com/?p=source.git%3Ba=blob%3Bf=doc/bugs/dashed_ssh_hostname_security_hole.mdwn
- http://www.debian.org/security/2017/dsa-4010
