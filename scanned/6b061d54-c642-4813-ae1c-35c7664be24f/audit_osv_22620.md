# [M] CVE-2022-3437

## Summary
Severity: Medium
Advisory: CVE-2022-3437
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2022-3437
Type: osv

## Details
A heap-based buffer overflow vulnerability was found in Samba within the GSSAPI unwrap_des() and unwrap_des3() routines of Heimdal. The DES and Triple-DES decryption routines in the Heimdal GSSAPI library allow a length-limited write buffer overflow on malloc() allocated memory when presented with a maliciously small packet. This flaw allows a remote user to send specially crafted malicious data to the application, possibly resulting in a denial of service (DoS) attack.

## References
- https://access.redhat.com/security/cve/CVE-2022-3437
- https://www.samba.org/samba/security/CVE-2022-3437.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3437.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3437
- https://security.gentoo.org/glsa/202309-06
- https://security.gentoo.org/glsa/202310-06
- https://security.netapp.com/advisory/ntap-20230216-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=2137774
- http://www.openwall.com/lists/oss-security/2023/02/08/1
- https://lists.debian.org/debian-lts-announce/2024/04/msg00015.html
