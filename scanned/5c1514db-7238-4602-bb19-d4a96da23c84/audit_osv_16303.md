# [H] CVE-2019-5094

## Summary
Severity: High
Advisory: CVE-2019-5094
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-09-24
Source: https://osv.dev/vulnerability/CVE-2019-5094
Type: osv

## Details
An exploitable code execution vulnerability exists in the quota file functionality of E2fsprogs 1.45.3. A specially crafted ext4 partition can cause an out-of-bounds write on the heap, resulting in code execution. An attacker can corrupt a partition to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2AKETJ6BREDUHRWQTV35SPGG5C6H7KSI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6DOBCYQKCTTWXBLMUPJ5TX3FY7JNCOKY/
- https://lists.debian.org/debian-lts-announce/2019/09/msg00029.html
- https://seclists.org/bugtraq/2019/Sep/58
- https://security.gentoo.org/glsa/202003-05
- https://security.netapp.com/advisory/ntap-20200115-0002/
- https://usn.ubuntu.com/4142-1/
- https://usn.ubuntu.com/4142-2/
- https://www.debian.org/security/2019/dsa-4535
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0887
