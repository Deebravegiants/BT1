# [H] CVE-2021-27292

## Summary
Severity: High
Advisory: CVE-2021-27292
Aliases: GHSA-78cj-fxph-m83p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-17
Source: https://osv.dev/vulnerability/CVE-2021-27292
Type: osv

## Details
ua-parser-js >= 0.7.14, fixed in 0.7.24, uses a regular expression which is vulnerable to denial of service. If an attacker sends a malicious User-Agent header, ua-parser-js will get stuck processing it for an extended period of time.

## References
- https://github.com/faisalman/ua-parser-js/commit/809439e20e273ce0d25c1d04e111dcf6011eb566
- https://github.com/pygments/pygments/commit/2e7e8c4a7b318f4032493773732754e418279a14
- https://gist.github.com/b-c-ds/6941d80d6b4e694df4bc269493b7be76
