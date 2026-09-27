# [M] CVE-2016-3189

## Summary
Severity: Medium
Advisory: CVE-2016-3189
Aliases: PSF-2016-5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-06-30
Source: https://osv.dev/vulnerability/CVE-2016-3189
Type: osv

## Details
Use-after-free vulnerability in bzip2recover in bzip2 1.0.6 allows remote attackers to cause a denial of service (crash) via a crafted bzip2 file, related to block ends set to before the start of the block.

## References
- https://lists.apache.org/thread.html/r19b4a70ac52093115fd71d773a7a4f579599e6275a13cfcf6252c3e3%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r1dc4c9b3bd559301bdb1557245f78b8910146efb1ee534b774c5f6af%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r481cda41fefb03e04c51484ed14421d812e5ce9e0972edff10f37260%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r4ad2ea01354e394b7fa8c78a184b7e1634d51be9bc0e9e4d7e6c9305%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r5f7ac2bd631ccb12ced65b71ff11f94e76d05b22000795e4a7b61203%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r5f80cf3ade5bb73410643e885fe6b7bf9f0222daf3533e42c7ae240c%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r6e3962fc9f6a79851f70cffdec5759065969cec9c6708b964464b301%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/ra0adb9653c7de9539b93cc8434143b655f753b9f60580ff260becb2b%40%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/redf17d8ad16140733b25ca402ae825d6dfa9b85f73d9fb3fd0c75d73%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rffebcbeaace56ff1fed7916700d2f414ca1366386fb1293e99b3e31e%40%3Cjira.kafka.apache.org%3E
- http://packetstormsecurity.com/files/153644/Slackware-Security-Advisory-bzip2-Updates.html
- http://packetstormsecurity.com/files/153957/FreeBSD-Security-Advisory-FreeBSD-SA-19-18.bzip2.html
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91297
- http://www.securitytracker.com/id/1036132
- https://lists.debian.org/debian-lts-announce/2019/06/msg00021.html
- https://seclists.org/bugtraq/2019/Aug/4
- https://seclists.org/bugtraq/2019/Jul/22
- https://security.FreeBSD.org/advisories/FreeBSD-SA-19:18.bzip2.asc
- https://security.gentoo.org/glsa/201708-08
