# [M] Authorization bypass in Ant Media Server

## Summary
Severity: Medium
Advisory: CVE-2024-3462
Aliases: GHSA-g95v-3pj6-j433
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-3462
Type: osv

## Details
Ant Media Server Community Edition in a default configuration is vulnerable to an improper HTTP header based authorization, leading to a possible use of non-administrative API calls reserved only for authorized users. 
All versions up to 2.9.0 (tested) and possibly newer ones are believed to be vulnerable as the vendor has not confirmed releasing a patch.

## References
- https://antmedia.io/
- https://cert.pl/en/posts/2024/05/CVE-2024-3462
- https://cert.pl/posts/2024/05/CVE-2024-3462
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3462.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3462
- https://github.com/ant-media/Ant-Media-Server
