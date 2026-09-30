# [H] golang.org/x/net/http vulnerable to ping floods

## Summary
Severity: High
Advisory: GHSA-hgr8-6h9x-f7q9
CVE: CVE-2019-9512
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hgr8-6h9x-f7q9
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.0.0-20190813141303-74dc4d7220e7

## Details
Some HTTP/2 implementations are vulnerable to ping floods, potentially leading to a denial of service. The attacker sends continual pings to an HTTP/2 peer, causing the peer to build an internal queue of responses. Depending on how efficiently this data is queued, this can consume excess CPU, memory, or both.

### Specific Go Packages Affected
golang.org/x/net/http2

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9512
- https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-002.md
- https://go.dev/cl/190137
- https://go.dev/issue/33606
- https://go.googlesource.com/go/+/145e193131eb486077b66009beb051aba07c52a5
- https://groups.google.com/g/golang-announce/c/65QixT3tcmg/m/DrFiG6vvCwAJ
- https://kb.cert.org/vuls/id/605641
- https://kc.mcafee.com/corporate/index?page=content&id=SB10296
- https://lists.apache.org/thread.html/392108390cef48af647a2e47b7fd5380e050e35ae8d1aa2030254c04@%3Cusers.trafficserver.apache.org%3E
- https://lists.apache.org/thread.html/ad3d01e767199c1aed8033bb6b3f5bf98c011c7c536f07a5d34b3c19@%3Cannounce.trafficserver.apache.org%3E
- https://lists.apache.org/thread.html/bde52309316ae798186d783a5e29f4ad1527f61c9219a289d0eee0a7@%3Cdev.trafficserver.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/12/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4BBP27PZGSY6OP6D26E5FW4GZKBFHNU7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4ZQGHE3WTYLYAYJEIDJVF2FIGQTAYPMC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CMNFX5MNYRWWIMO4BTKYQCGUDMHO3AXP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYO6E3H34C346D2E443GLXK7OK6KIYIQ
- https://pkg.go.dev/vuln/GO-2022-0536
- https://seclists.org/bugtraq/2019/Aug/24
- https://seclists.org/bugtraq/2019/Aug/31
- https://seclists.org/bugtraq/2019/Aug/43
