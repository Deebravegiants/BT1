# [C] CVE-2019-18823

## Summary
Severity: Critical
Advisory: CVE-2019-18823
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2019-18823
Type: osv

## Details
HTCondor up to and including stable series 8.8.6 and development series 8.9.4 has Incorrect Access Control. It is possible to use a different authentication method to submit a job than the administrator has specified. If the administrator has configured the READ or WRITE methods to include CLAIMTOBE, then it is possible to impersonate another user to the condor_schedd. (For example to submit or remove jobs)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3EOTJJOSMYKXIYXWSG3H4KN332EDSEB6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BL5YCZXYS67MLJSHR4OLSWVHBE6PZJSB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VMPZ7XPOPA4JGAQAUJ4K7JV653DSCIDK/
- https://research.cs.wisc.edu/htcondor/
- https://lists.debian.org/debian-lts-announce/2021/08/msg00000.html
- https://research.cs.wisc.edu/htcondor/new.html
- https://research.cs.wisc.edu/htcondor/security/vulnerabilities/HTCONDOR-2020-0001.html
- https://research.cs.wisc.edu/htcondor/security/vulnerabilities/HTCONDOR-2020-0002.html
- https://research.cs.wisc.edu/htcondor/security/vulnerabilities/HTCONDOR-2020-0003.html
- https://research.cs.wisc.edu/htcondor/security/vulnerabilities/HTCONDOR-2020-0004.html
- https://www.debian.org/security/2022/dsa-5144
