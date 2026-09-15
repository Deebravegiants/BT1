# [M] CVE-2022-42319

## Summary
Severity: Medium
Advisory: CVE-2022-42319
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42319
Type: osv

## Details
Xenstore: Guests can cause Xenstore to not free temporary memory When working on a request of a guest, xenstored might need to allocate quite large amounts of memory temporarily. This memory is freed only after the request has been finished completely. A request is regarded to be finished only after the guest has read the response message of the request from the ring page. Thus a guest not reading the response can cause xenstored to not free the temporary memory. This can result in memory shortages causing Denial of Service (DoS) of xenstored.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- http://www.openwall.com/lists/oss-security/2022/11/01/6
- https://xenbits.xenproject.org/xsa/advisory-416.txt
- http://xenbits.xen.org/xsa/advisory-416.html
