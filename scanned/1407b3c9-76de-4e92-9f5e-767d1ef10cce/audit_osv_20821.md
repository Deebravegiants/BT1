# [M] CVE-2021-3744

## Summary
Severity: Medium
Advisory: CVE-2021-3744
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-3744
Type: osv

## Details
A memory leak flaw was found in the Linux kernel in the ccp_run_aes_gcm_cmd() function in drivers/crypto/ccp/ccp-ops.c, which allows attackers to cause a denial of service (memory consumption). This vulnerability is similar with the older CVE-2019-18808.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SYKURLXBB2555ASWMPDNMBUPD6AG2JKQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LAT3RERO6QBKSPJBNNRWY3D4NCGTFOS7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7BLLVKYAIETEORUPTFO3TR3C33ZPFXQM/
- https://www.debian.org/security/2022/dsa-5096
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2000627
- https://seclists.org/oss-sec/2021/q3/164
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://github.com/torvalds/linux/commit/505d9dcb0f7ddf9d075e729523a33d38642ae680
- https://kernel.googlesource.com/pub/scm/linux/kernel/git/herbert/crypto-2.6/+/505d9dcb0f7ddf9d075e729523a33d38642ae680%5E%21/#F0
- http://www.openwall.com/lists/oss-security/2021/09/14/1
