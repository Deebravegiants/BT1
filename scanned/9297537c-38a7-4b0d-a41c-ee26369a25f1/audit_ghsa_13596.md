# [H] HTTP/2 rapid reset can cause excessive work in net/http

## Summary
Severity: High
Advisory: GHSA-4374-p667-p6c8
CVE: CVE-2023-39325
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-11
Source: https://github.com/advisories/GHSA-4374-p667-p6c8
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.17.0

## Details
A malicious HTTP/2 client which rapidly creates requests and immediately resets them can cause excessive server resource consumption. While the total number of requests is bounded by the http2.Server.MaxConcurrentStreams setting, resetting an in-progress request allows the attacker to create a new request while the existing one is still executing. 

With the fix applied, HTTP/2 servers now bound the number of simultaneously executing handler goroutines to the stream concurrency limit (MaxConcurrentStreams). New requests arriving when at the limit (which can only happen after the client has reset an existing, in-flight request) will be queued until a handler exits. If the request queue grows too large, the server will terminate the connection. 

This issue is also fixed in golang.org/x/net/http2 for users manually configuring HTTP/2.

The default stream concurrency limit is 250 streams (requests) per HTTP/2 connection. This value may be adjusted using the golang.org/x/net/http2 package; see the Server.MaxConcurrentStreams setting and the ConfigureServer function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39325
- https://github.com/golang/go/issues/63417
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NG7IMPL55MVWU3LCI4JQJT3K2U5CHDV7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ODBY7RVMGZCBSTWF2OZGIZS57FNFUL67
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OXGWPQOJ3JNDW2XIYKIVJ7N7QUIFNM2Q
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PJCUNGIQDUMZ4Z6HWVYIMR66A35F5S74
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QF5QSYAOPDOWLY6DUHID56Q4HQFYB45I
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QXOU2JZUBEBP7GBKAYIJRPRBZSJCD7ST
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R3UETKPUB3V5JS5TLZOF3SMTGT5K5APS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/REMHVVIBDNKSRKNOTV7EQSB7CYQWOUOU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T7N5GV4CHH6WAGX3GFMDD3COEOVCZ4RI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ULQQONMSCQSH5Z5OWFFQHCGEZ3NL4DRJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UTT7DG3QOF5ZNJLUGHDNLRUIN6OWZARP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W2LZSWTV4NV4SNQARNXG5T6LRHP26EW2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WCNCBYKZXLDFGAJUB7ZP5VLC3YTHJNVH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XFOIBB4YFICHDM7IBOP7PWXW3FX4HLL2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XTNLSL44Y5FB6JWADSZH6DCV4JJAAEQY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YJWHBLVZDM5KQSDFRBFRKU5KSSOLIRQ4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YRKEXKANQ7BKJW2YTAMP625LJUJZLJ4P
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZSVEMQV5ROY5YW5QE3I57HT3ITWG5GCV
