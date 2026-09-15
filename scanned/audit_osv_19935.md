# [H] CVE-2021-28092

## Summary
Severity: High
Advisory: CVE-2021-28092
Aliases: GHSA-7r28-3m3f-r2pr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-12
Source: https://osv.dev/vulnerability/CVE-2021-28092
Type: osv

## Details
The is-svg package 2.1.0 through 4.2.1 for Node.js uses a regular expression that is vulnerable to Regular Expression Denial of Service (ReDoS). If an attacker provides a malicious string, is-svg will get stuck processing the input for a very long time.

## References
- https://www.npmjs.com/package/is-svg
- https://github.com/sindresorhus/is-svg/releases
- https://github.com/sindresorhus/is-svg/releases/tag/v4.2.2
- https://security.netapp.com/advisory/ntap-20210513-0008/
