# [M] CVE-2013-4584

## Summary
Severity: Medium
Advisory: CVE-2013-4584
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-11-15
Source: https://osv.dev/vulnerability/CVE-2013-4584
Type: osv

## Details
Perdition before 2.2 may have weak security when handling outbound connections, caused by an error in the STARTTLS IMAP and POP server. ssl_outgoing_ciphers not being applied to STARTTLS connections

## References
- http://www.openwall.com/lists/oss-security/2013/11/15/6
- http://www.securityfocus.com/bid/63696
- https://exchange.xforce.ibmcloud.com/vulnerabilities/89184
- https://security-tracker.debian.org/tracker/CVE-2013-4584
- http://www.openwall.com/lists/oss-security/2013/11/15/6
- http://www.openwall.com/lists/oss-security/2013/11/15/6
- https://github.com/horms/perdition/commit/62a0ce94aeb7dd99155882956ce9e327ab914ddf
- https://access.redhat.com/security/cve/cve-2013-4584
