# [M] CVE-2021-28700

## Summary
Severity: Medium
Advisory: CVE-2021-28700
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-28700
Type: osv

## Details
xen/arm: No memory limit for dom0less domUs The dom0less feature allows an administrator to create multiple unprivileged domains directly from Xen. Unfortunately, the memory limit from them is not set. This allow a domain to allocate memory beyond what an administrator originally configured.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2VQCFAPBNGBBAOMJZG6QBREOG5IIDZID/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FZCNPSRPGFCQRYE2BI4D4Q4SCE56ANV2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LPRVHW4J4ZCPPOHZEWP5MOJT7XDGFFPJ/
- https://security.gentoo.org/glsa/202208-23
- https://www.debian.org/security/2021/dsa-4977
- https://xenbits.xenproject.org/xsa/advisory-383.txt
