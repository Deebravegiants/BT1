# [H] CVE-2018-1000621

## Summary
Severity: High
Advisory: CVE-2018-1000621
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-09
Source: https://osv.dev/vulnerability/CVE-2018-1000621
Type: osv

## Details
Mycroft AI mycroft-core version 18.2.8b and earlier contains a Incorrect Access Control vulnerability in Websocket configuration that can result in code execution. This impacts ONLY the Mycroft for Linux and "non-enclosure" installs - Mark 1 and Picroft unaffected. This attack appear to be exploitable remote access to the unsecured websocket server. This vulnerability appears to have been fixed in No fix currently available.

## References
- https://community.mycroft.ai/t/zero-click-remote-code-execution-in-mycroft-ai-vocal-assistant/3930/13
- https://github.com/Nhoya/MycroftAI-RCE
