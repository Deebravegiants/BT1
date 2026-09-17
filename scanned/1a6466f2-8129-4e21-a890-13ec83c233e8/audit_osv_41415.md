# [C] gpsd gpsprof Code Injection via SKY.satellites used Field

## Summary
Severity: Critical
Advisory: CVE-2026-60122
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-60122
Type: osv

## Details
gpsd through release-3.27.5, fixed at commit 4c06658, contains a code injection vulnerability in the gpsprof utility that allows an attacker who controls GPS input data to execute arbitrary OS commands by injecting malicious content into the SKY.satellites[].used field, which is inserted unsanitized into a gnuplot heredoc data block. Attackers can supply a used value containing the string EOD to terminate the heredoc early and append gnuplot system() calls, achieving OS command execution as the user running gpsprof when the generated plot script is processed by gnuplot in polar mode.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60122.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-60122
- https://www.vulncheck.com/advisories/gpsd-gpsprof-code-injection-via-sky-satellites-used-field
- https://gitlab.com/gpsd/gpsd/-/work_items/406
- https://gitlab.com/gpsd/gpsd/-/commit/5a9c44a42136b9bb98d460a8a716e9fd344a8d93
- https://github.com/ntpsec/gpsd
