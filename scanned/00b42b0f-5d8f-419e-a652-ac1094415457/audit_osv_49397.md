# [C] CVE-2019-11708

## Summary
Severity: Critical
Advisory: CVE-2019-11708
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11708
Type: osv

## Details
Insufficient vetting of parameters passed with the Prompt:Open IPC message between child and parent processes can result in the non-sandboxed parent process opening web content chosen by a compromised child process. When combined with additional vulnerabilities this could result in executing arbitrary code on the user's computer. This vulnerability affects Firefox ESR < 60.7.2, Firefox < 67.0.4, and Thunderbird < 60.7.2.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-11708
- https://security.gentoo.org/glsa/201908-12
- https://www.mozilla.org/security/advisories/mfsa2019-19/
- https://www.mozilla.org/security/advisories/mfsa2019-20/
- http://packetstormsecurity.com/files/155592/Mozilla-Firefox-Windows-64-Bit-Chain-Exploit.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1559858
