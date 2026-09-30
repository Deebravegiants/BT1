# [C] CVE-2021-3401

## Summary
Severity: Critical
Advisory: CVE-2021-3401
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-04
Source: https://osv.dev/vulnerability/CVE-2021-3401
Type: osv

## Details
Bitcoin Core before 0.19.0 might allow remote attackers to execute arbitrary code when another application unsafely passes the -platformpluginpath argument to the bitcoin-qt program, as demonstrated by an x-scheme-handler/bitcoin handler for a .desktop file or a web browser. NOTE: the discoverer states "I believe that this vulnerability cannot actually be exploited."

## References
- https://achow101.com/2021/02/0.18-uri-vuln
- https://github.com/bitcoin/bitcoin/pull/16578
