# [H] CVE-2022-42309

## Summary
Severity: High
Advisory: CVE-2022-42309
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42309
Type: osv

## Details
Xenstore: Guests can crash xenstored Due to a bug in the fix of XSA-115 a malicious guest can cause xenstored to use a wrong pointer during node creation in an error path, resulting in a crash of xenstored or a memory corruption in xenstored causing further damage. Entering the error path can be controlled by the guest e.g. by exceeding the quota value of maximum nodes per domain.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- http://www.openwall.com/lists/oss-security/2022/11/01/4
- https://xenbits.xenproject.org/xsa/advisory-414.txt
- http://xenbits.xen.org/xsa/advisory-414.html
