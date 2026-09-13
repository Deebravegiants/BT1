# [H] CVE-2022-33745

## Summary
Severity: High
Advisory: CVE-2022-33745
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-07-26
Source: https://osv.dev/vulnerability/CVE-2022-33745
Type: osv

## Details
insufficient TLB flush for x86 PV guests in shadow mode For migration as well as to work around kernels unaware of L1TF (see XSA-273), PV guests may be run in shadow paging mode. To address XSA-401, code was moved inside a function in Xen. This code movement missed a variable changing meaning / value between old and new code positions. The now wrong use of the variable did lead to a wrong TLB flush condition, omitting flushes where such are necessary.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HUFIMNGYP5VQAA6KE3T2I5GW6UP6F7BS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MYI3OMJ7RIZNL3C6GUWNANNPEUUID6FM/
- https://www.debian.org/security/2022/dsa-5272
- https://xenbits.xenproject.org/xsa/advisory-408.txt
- http://www.openwall.com/lists/oss-security/2022/07/26/2
- http://www.openwall.com/lists/oss-security/2022/07/26/3
- http://xenbits.xen.org/xsa/advisory-408.html
