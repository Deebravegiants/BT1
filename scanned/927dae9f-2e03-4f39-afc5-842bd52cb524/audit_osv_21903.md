# [H] Use of a Broken or Risky Cryptographic Algorithm in gnuboard/gnuboard5

## Summary
Severity: High
Advisory: CVE-2022-1252
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2022-04-11
Source: https://osv.dev/vulnerability/CVE-2022-1252
Type: osv

## Details
Use of a Broken or Risky Cryptographic Algorithm in GitHub repository gnuboard/gnuboard5 prior to and including 5.5.5. A vulnerability in gnuboard v5.5.5 and below uses weak encryption algorithms leading to sensitive information exposure. This allows an attacker to derive the email address of any user, including when the 'Let others see my information.' box is ticked off. Or to send emails to any email address, with full control of its contents

## References
- https://0g.vc/posts/insecure-cipher-gnuboard5/
- https://huntr.dev/bounties/c8c2c3e1-67d0-4a11-a4d4-11af567a9ebb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1252.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1252
