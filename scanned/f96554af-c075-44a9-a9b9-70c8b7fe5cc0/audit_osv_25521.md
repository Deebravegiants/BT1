# [C] CVE-2023-38408

## Summary
Severity: Critical
Advisory: CVE-2023-38408
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2023-38408
Type: osv

## Details
The PKCS#11 feature in ssh-agent in OpenSSH before 9.3p2 has an insufficiently trustworthy search path, leading to remote code execution if an agent is forwarded to an attacker-controlled system. (Code in /usr/lib is not necessarily safe for loading into ssh-agent.) NOTE: this issue exists because of an incomplete fix for CVE-2016-10009.

## References
- http://packetstormsecurity.com/files/173661/OpenSSH-Forwarded-SSH-Agent-Remote-Code-Execution.html
- https://news.ycombinator.com/item?id=36790196
- https://support.apple.com/kb/HT213940
- https://www.openssh.com/security.html
- https://www.openssh.com/txt/release-9.3p2
- https://www.qualys.com/2023/07/19/cve-2023-38408/rce-openssh-forwarded-ssh-agent.txt
- https://www.vicarius.io/vsociety/posts/exploring-opensshs-agent-forwarding-rce-cve-2023-38408
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38408.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CEBTJJINE2I3FHAUKKNQWMFGYMLSMWKQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RAXVQS6ZYTULFAK3TEJHRLKZALJS3AOU/
- https://nvd.nist.gov/vuln/detail/CVE-2023-38408
- https://security.gentoo.org/glsa/202307-01
- https://security.netapp.com/advisory/ntap-20230803-0010/
- https://github.com/openbsd/src/commit/7bc29a9d5cd697290aa056e94ecee6253d3425f8
- https://github.com/openbsd/src/commit/f03a4faa55c4ce0818324701dadbf91988d7351d
- https://github.com/openbsd/src/commit/f8f5a6b003981bb824329dc987d101977beda7ca
- http://www.openwall.com/lists/oss-security/2023/07/20/1
- http://www.openwall.com/lists/oss-security/2023/07/20/2
- http://www.openwall.com/lists/oss-security/2023/09/22/11
- http://www.openwall.com/lists/oss-security/2023/09/22/9
