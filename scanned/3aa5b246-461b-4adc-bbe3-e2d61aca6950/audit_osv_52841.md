# [H] CVE-2022-1652

## Summary
Severity: High
Advisory: CVE-2022-1652
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-1652
Type: osv

## Details
Linux Kernel could allow a local attacker to execute arbitrary code on the system, caused by a concurrency use-after-free flaw in the bad_flp_intr function. By executing a specially-crafted program, an attacker could exploit this vulnerability to execute arbitrary code or cause a denial of service condition on the system.

## References
- https://francozappa.github.io/about-bias/
- https://kb.cert.org/vuls/id/647177/
- https://security.netapp.com/advisory/ntap-20220722-0002/
- https://www.debian.org/security/2022/dsa-5173
- https://bugzilla.redhat.com/show_bug.cgi?id=1832397
