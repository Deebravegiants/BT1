# [M] BIT-jenkins-2020-2231

## Summary
Severity: Medium
Advisory: BIT-jenkins-2020-2231
Aliases: CVE-2020-2231, GHSA-jpvq-v729-7j2h
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2020-2231
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.251.1

## Details
Jenkins 2.251 and earlier, LTS 2.235.3 and earlier does not escape the remote address of the host starting a build via 'Trigger builds remotely', resulting in a stored cross-site scripting (XSS) vulnerability exploitable by users with Job/Configure permission or knowledge of the Authentication Token.

## References
- http://packetstormsecurity.com/files/160616/Jenkins-2.251-LTS-2.235.3-Cross-Site-Scripting.html
- http://www.openwall.com/lists/oss-security/2020/08/12/4
- https://jenkins.io/security/advisory/2020-08-12/#SECURITY-1960
- https://nvd.nist.gov/vuln/detail/CVE-2020-2231
