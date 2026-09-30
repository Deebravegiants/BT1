# [M] Insecure EBICS messages encryption implementation in ebics-java/ebics-java-client could allow an adjacent attacker to decrypt EBICS payloads

## Summary
Severity: Medium
Advisory: CVE-2022-1279
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2022-1279
Type: osv

## Details
A vulnerability in the encryption implementation of EBICS messages in the open source librairy ebics-java/ebics-java-client allows an attacker sniffing network traffic to decrypt EBICS payloads. This issue affects: ebics-java/ebics-java-client versions prior to 1.2.

## References
- https://github.com/ebics-java/ebics-java-client/releases/tag/1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1279.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1279
