# [M] PHZ76 RtspServer RtspMesaage.cpp ParseRequestLine stack-based overflow

## Summary
Severity: Medium
Advisory: CVE-2023-6888
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-12-17
Source: https://osv.dev/vulnerability/CVE-2023-6888
Type: osv

## Details
A vulnerability classified as critical was found in PHZ76 RtspServer 1.0.0. This vulnerability affects the function ParseRequestLine of the file RtspMesaage.cpp. The manipulation leads to stack-based buffer overflow. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. The identifier of this vulnerability is VDB-248248. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- http://www.huiyao.love/2023/12/08/rtspserver-stackoverflow-vulnerability/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6888.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6888
- https://vuldb.com/?id.248248
- https://vuldb.com/?ctiid.248248
- https://github.com/hu1y40/PoC/blob/main/rtspserver_stackoverflow_poc.py
