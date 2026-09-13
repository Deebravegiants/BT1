# [H] Code Injection in Combodo iTop

## Summary
Severity: High
Advisory: CVE-2022-24780
Aliases: GHSA-v97m-wgxq-rh54
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2022-24780
Type: osv

## Details
Combodo iTop is a web based IT Service Management tool. In versions prior to 2.7.6 and 3.0.0, users of the iTop user portal can send TWIG code to the server by forging specific http queries, and execute arbitrary code on the server using http server user privileges. This issue is fixed in versions 2.7.6 and 3.0.0. There are currently no known workarounds.

## References
- http://packetstormsecurity.com/files/167236/iTop-Remote-Command-Execution.html
- https://markus-krell.de/itop-template-injection-inside-customer-portal/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24780.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-v97m-wgxq-rh54
- https://nvd.nist.gov/vuln/detail/CVE-2022-24780
- https://github.com/Combodo/iTop/commit/93f273a28778e5da8e51096f021d2dc1adbf4ef3
- https://github.com/Combodo/iTop/commit/b6fac4b411b8d145fc30fa35c66b51243eafd06b
- https://github.com/Combodo/iTop/commit/eb2a615bd28100442c7f6171707bb40884af2305
