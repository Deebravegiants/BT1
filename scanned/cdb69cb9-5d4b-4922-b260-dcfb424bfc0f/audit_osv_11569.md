# [H] CVE-2017-8804

## Summary
Severity: High
Advisory: CVE-2017-8804
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-07
Source: https://osv.dev/vulnerability/CVE-2017-8804
Type: osv

## Details
The xdr_bytes and xdr_string functions in the GNU C Library (aka glibc or libc6) 2.25 mishandle failures of buffer deserialization, which allows remote attackers to cause a denial of service (virtual memory allocation, or memory consumption if an overcommit setting is not used) via a crafted UDP packet to port 111, a related issue to CVE-2017-8779. NOTE: [Information provided from upstream and references

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00049.html
- http://www.securityfocus.com/bid/98339
- https://seclists.org/oss-sec/2017/q2/228
- https://sourceware.org/legacy-ml/libc-alpha/2017-05/msg00128.html
- https://sourceware.org/legacy-ml/libc-alpha/2017-05/msg00129.html
- http://www.openwall.com/lists/oss-security/2017/05/05/2
- https://bugzilla.suse.com/show_bug.cgi?id=1037559#c7
- https://sourceware.org/bugzilla/show_bug.cgi?id=21461
- https://sourceware.org/ml/libc-alpha/2017-05/msg00105.html
