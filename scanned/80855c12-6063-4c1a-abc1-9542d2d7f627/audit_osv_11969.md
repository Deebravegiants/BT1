# [H] CVE-2018-1000400

## Summary
Severity: High
Advisory: CVE-2018-1000400
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-1000400
Type: osv

## Details
Kubernetes CRI-O version prior to 1.9 contains a Privilege Context Switching Error (CWE-270) vulnerability in the handling of ambient capabilities that can result in containers running with elevated privileges, allowing users abilities they should not have. This attack appears to be exploitable via container execution. This vulnerability appears to have been fixed in 1.9.

## References
- http://www.securityfocus.com/bid/104262
- https://github.com/kubernetes-incubator/cri-o/pull/1558/files
