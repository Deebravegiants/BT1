# [H] CVE-2017-7393

## Summary
Severity: High
Advisory: CVE-2017-7393
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-01
Source: https://osv.dev/vulnerability/CVE-2017-7393
Type: osv

## Details
In TigerVNC 1.7.1 (VNCSConnectionST.cxx VNCSConnectionST::fence), an authenticated client can cause a double free, leading to denial of service or potentially code execution.

## References
- http://www.securityfocus.com/bid/97305
- https://access.redhat.com/errata/RHSA-2017:2000
- https://security.gentoo.org/glsa/201801-13
- https://github.com/TigerVNC/tigervnc/pull/438
