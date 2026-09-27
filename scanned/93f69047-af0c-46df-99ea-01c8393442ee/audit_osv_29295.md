# [H] CVE-2024-4140

## Summary
Severity: High
Advisory: CVE-2024-4140
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-02
Source: https://osv.dev/vulnerability/CVE-2024-4140
Type: osv

## Details
An excessive memory use issue (CWE-770) exists in Email-MIME, before version 1.954, which can cause denial of service when parsing multipart MIME messages. The patch set (from 2020 and 2024) limits excessive depth and the total number of parts.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UFD5BWGYAVLW6IO4SUNLTJCFFLHZYQGT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YHXHDLPZ6JV4KK3Q43O6TE3WOBAIUQRC/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4140.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4140
- https://bugs.debian.org/960062
- https://github.com/rjbs/Email-MIME/issues/66
- https://github.com/rjbs/Email-MIME/pull/80
- https://www.cve.org/CVERecord?id=CVE-2024-4140
- https://github.com/rjbs/Email-MIME/commit/02bf3e26812c8f38a86a33c168571f9783365df2
- https://github.com/rjbs/Email-MIME/commit/3a12edd119e493156a5a05e45dd50f4e36b702e8
- https://github.com/rjbs/Email-MIME/commit/3dcf096eeccb8e4dd42738de676c8f4a5aa7a531
- https://github.com/rjbs/Email-MIME/commit/7e96ecfa1da44914a407f82ae98ba817bba08f2d
- https://github.com/rjbs/Email-MIME/commit/b2cb62f19e12580dd235f79e2546d44a6bec54d1
- https://github.com/rjbs/Email-MIME/commit/fc0fededd24a71ccc51bcd8b1e486385d09aae63
- https://github.com/rjbs/Email-MIME
