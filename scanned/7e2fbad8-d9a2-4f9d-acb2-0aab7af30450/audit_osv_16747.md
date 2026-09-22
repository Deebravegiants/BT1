# [C] CVE-2019-9535

## Summary
Severity: Critical
Advisory: CVE-2019-9535
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-9535
Type: osv

## Details
A vulnerability exists in the way that iTerm2 integrates with tmux's control mode, which may allow an attacker to execute arbitrary commands by providing malicious output to the terminal. This affects versions of iTerm2 up to and including 3.3.5. This vulnerability may allow an attacker to execute arbitrary commands on their victim's computer by providing malicious output to the terminal. It could be exploited using command-line utilities that print attacker-controlled content.

## References
- https://groups.google.com/forum/#%21topic/iterm2-discuss/57k_AuLdQa4
- https://kb.cert.org/vuls/id/763073/
- https://blog.mozilla.org/security/2019/10/09/iterm2-critical-issue-moss-audit/
