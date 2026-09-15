# [H] Apache Traffic Server: HTTP/2 CONTINUATION frames can be utilized for DoS attack

## Summary
Severity: High
Advisory: CVE-2024-31309
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-31309
Type: osv

## Details
HTTP/2 CONTINUATION DoS attack can cause Apache Traffic Server to consume more resources on the server.  Version from 8.0.0 through 8.1.9, from 9.0.0 through 9.2.3 are affected.

Users can set a new setting (proxy.config.http2.max_continuation_frames_per_minute) to limit the number of CONTINUATION frames per minute.  ATS does have a fixed amount of memory a request can use and ATS adheres to these limits in previous releases.
Users are recommended to upgrade to versions 8.1.10 or 9.2.4 which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/04/03/16
- http://www.openwall.com/lists/oss-security/2024/04/10/7
- https://lists.debian.org/debian-lts-announce/2024/04/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PBKLPQ6ECG4PGEPRCYI3Y3OITNDEFCCV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QV77HYM7ARSTL3B6U3IFG7PHDU65WL4I/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T3XON6RM5ZKCZ6K6NB7BOTAWMJQKXJDO/
- https://www.kb.cert.org/vuls/id/421644
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31309.json
- https://lists.apache.org/thread/f9qh3g3jvy153wh82pz4onrfj1wh13kc
- https://nvd.nist.gov/vuln/detail/CVE-2024-31309
