# [M] CVE-2021-28698

## Summary
Severity: Medium
Advisory: CVE-2021-28698
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-28698
Type: osv

## Details
long running loops in grant table handling In order to properly monitor resource use, Xen maintains information on the grant mappings a domain may create to map grants offered by other domains. In the process of carrying out certain actions, Xen would iterate over all such entries, including ones which aren't in use anymore and some which may have been created but never used. If the number of entries for a given domain is large enough, this iterating of the entire table may tie up a CPU for too long, starving other domains or causing issues in the hypervisor itself. Note that a domain may map its own grants, i.e. there is no need for multiple domains to be involved here. A pair of "cooperating" guests may, however, cause the effects to be more severe.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FZCNPSRPGFCQRYE2BI4D4Q4SCE56ANV2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LPRVHW4J4ZCPPOHZEWP5MOJT7XDGFFPJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2VQCFAPBNGBBAOMJZG6QBREOG5IIDZID/
- https://security.gentoo.org/glsa/202208-23
- https://www.debian.org/security/2021/dsa-4977
- https://xenbits.xenproject.org/xsa/advisory-380.txt
- http://www.openwall.com/lists/oss-security/2021/09/01/2
