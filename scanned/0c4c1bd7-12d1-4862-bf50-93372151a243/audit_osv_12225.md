# [C] CVE-2018-10933

## Summary
Severity: Critical
Advisory: CVE-2018-10933
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-10933
Type: osv

## Details
A vulnerability was found in libssh's server-side state machine before versions 0.7.6 and 0.8.4. A malicious client could create channels without first performing authentication, resulting in unauthorized access.

## References
- http://www.securityfocus.com/bid/105677
- https://lists.debian.org/debian-lts-announce/2018/10/msg00010.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2018-0016
- https://security.netapp.com/advisory/ntap-20190118-0002/
- https://usn.ubuntu.com/3795-1/
- https://usn.ubuntu.com/3795-2/
- https://www.debian.org/security/2018/dsa-4322
- https://www.libssh.org/security/advisories/CVE-2018-10933.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10933
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.exploit-db.com/exploits/45638/
