# [H] CVE-2021-45444

## Summary
Severity: High
Advisory: CVE-2021-45444
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-02-14
Source: https://osv.dev/vulnerability/CVE-2021-45444
Type: osv

## Details
In zsh before 5.8.1, an attacker can achieve code execution if they control a command output inside the prompt, as demonstrated by a %F argument. This occurs because of recursive PROMPT_SUBST expansion.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2P3LPMGENEHKDWFO4MWMZSZL6G7Y4CV7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BWF3EXNBX5SVFDBL4ZFOD4GJBWFUKWN4/
- http://seclists.org/fulldisclosure/2022/May/33
- http://seclists.org/fulldisclosure/2022/May/35
- http://seclists.org/fulldisclosure/2022/May/38
- https://lists.debian.org/debian-lts-announce/2022/02/msg00020.html
- https://support.apple.com/kb/HT213255
- https://support.apple.com/kb/HT213256
- https://support.apple.com/kb/HT213257
- https://vuln.ryotak.me/advisories/63
- https://www.debian.org/security/2022/dsa-5078
- https://zsh.sourceforge.io/releases.html
