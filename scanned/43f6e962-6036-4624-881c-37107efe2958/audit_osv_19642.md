# [H] CVE-2021-23169

## Summary
Severity: High
Advisory: CVE-2021-23169
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-23169
Type: osv

## Details
A heap-buffer overflow was found in the copyIntoFrameBuffer function of OpenEXR in versions before 3.0.1. An attacker could use this flaw to execute arbitrary code with the permissions of the user running the application compiled against OpenEXR.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4KYNJSMVA6YJY5NMKDZ5SAISKZG2KCKC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BXFLD4ZAXKAIWO6ZPBCQEEDZB5IG676K/
- https://security.gentoo.org/glsa/202210-31
- https://bugzilla.redhat.com/show_bug.cgi?id=1947612
