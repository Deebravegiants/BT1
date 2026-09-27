# [H] CVE-2019-6477

## Summary
Severity: High
Advisory: CVE-2019-6477
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-6477
Type: osv

## Details
With pipelining enabled each incoming query on a TCP connection requires a similar resource allocation to a query received via UDP or via TCP without pipelining enabled. A client using a TCP-pipelined connection to a server could consume more resources than the server has been provisioned to handle. When a TCP connection with a large number of pipelined queries is closed, the load on the server releasing these multiple resources can cause it to become unresponsive, even for queries that can be answered authoritatively or from cache. (This is most likely to be perceived as an intermittent server problem).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L3DEMNZMKR57VQJCG5ZN55ZGTQRL2TFQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XGURMGQHX45KR4QDRCSUQHODUFOGNGAN/
- https://support.f5.com/csp/article/K15840535?utm_source=f5support&amp%3Butm_medium=RSS
- https://kb.isc.org/docs/cve-2019-6477
- https://www.debian.org/security/2020/dsa-4689
- https://www.synology.com/security/advisory/Synology_SA_19_39
