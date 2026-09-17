# [C] CVE-2022-36937

## Summary
Severity: Critical
Advisory: CVE-2022-36937
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-10
Source: https://osv.dev/vulnerability/CVE-2022-36937
Type: osv

## Details
HHVM 4.172.0 and all prior versions use TLS 1.0 for secure connections when handling tls:// URLs in the stream extension. TLS1.0 has numerous published vulnerabilities and is deprecated. HHVM 4.153.4, 4.168.2, 4.169.2, 4.170.2, 4.171.1, 4.172.1, 4.173.0 replaces TLS1.0 with TLS1.3.

Applications that call stream_socket_server or stream_socket_client functions with a URL starting with tls:// are affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36937.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-36937
- https://github.com/facebook/hhvm/commit/083f5ffdee661f61512909d16f9a5b98cff3cf0b
- https://hhvm.com/blog/2023/01/20/security-update.html
