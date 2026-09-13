# [C] JLSEC-2026-68

## Summary
Severity: Critical
Advisory: JLSEC-2026-68
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-68
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <9.3.2+0

## Details
The PKCS#11 feature in ssh-agent in OpenSSH before 9.3p2 has an insufficiently trustworthy search path, leading to remote code execution if an agent is forwarded to an attacker-controlled system. (Code in `/usr/lib` is not necessarily safe for loading into ssh-agent.) NOTE: this issue exists because of an incomplete fix for CVE-2016-10009.

## References
- http://packetstormsecurity.com/files/173661/OpenSSH-Forwarded-SSH-Agent-Remote-Code-Execution.html
- http://www.openwall.com/lists/oss-security/2023/07/20/1
- http://www.openwall.com/lists/oss-security/2023/07/20/2
- http://www.openwall.com/lists/oss-security/2023/09/22/11
- http://www.openwall.com/lists/oss-security/2023/09/22/9
- https://blog.qualys.com/vulnerabilities-threat-research/2023/07/19/cve-2023-38408-remote-code-execution-in-opensshs-forwarded-ssh-agent
- https://github.com/openbsd/src/commit/7bc29a9d5cd697290aa056e94ecee6253d3425f8
- https://github.com/openbsd/src/commit/f03a4faa55c4ce0818324701dadbf91988d7351d
- https://github.com/openbsd/src/commit/f8f5a6b003981bb824329dc987d101977beda7ca
- https://lists.debian.org/debian-lts-announce/2023/08/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CEBTJJINE2I3FHAUKKNQWMFGYMLSMWKQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RAXVQS6ZYTULFAK3TEJHRLKZALJS3AOU/
- https://news.ycombinator.com/item?id=36790196
- https://security.gentoo.org/glsa/202307-01
- https://security.netapp.com/advisory/ntap-20230803-0010/
- https://support.apple.com/kb/HT213940
- https://www.openssh.com/security.html
- https://www.openssh.com/txt/release-9.3p2
- https://www.qualys.com/2023/07/19/cve-2023-38408/rce-openssh-forwarded-ssh-agent.txt
- https://www.vicarius.io/vsociety/posts/exploring-opensshs-agent-forwarding-rce-cve-2023-38408
