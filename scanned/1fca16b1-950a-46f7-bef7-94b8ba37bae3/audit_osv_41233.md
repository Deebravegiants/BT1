# [C] gpsd gpsprof Command Injection via gnuplot plot title subtype field

## Summary
Severity: Critical
Advisory: CVE-2026-58459
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-58459
Type: osv

## Details
gpsd through release-3.27.5, fixed at commit 4c06658, contains a command injection vulnerability in gpsprof that allows attackers who control the GPS device subtype value to execute arbitrary shell commands by embedding backtick payloads in the gnuplot plot title without proper escaping. The subtype field sourced from a DEVICES JSON log entry or NMEA PGRMT sentence is written into a generated gnuplot program via a set title statement with only double-quote characters escaped, enabling arbitrary shell command execution as the user running gnuplot when the victim renders the generated plot through the gpsprof and gnuplot workflow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58459.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58459
- https://www.vulncheck.com/advisories/gpsd-gpsprof-command-injection-via-gnuplot-plot-title-subtype-field
- https://gitlab.com/gpsd/gpsd/-/work_items/404#note_3534119267
- https://github.com/ntpsec/gpsd/commit/1a6bb7bcbdf58aa940132e630870af061dc88537
- https://github.com/ntpsec/gpsd/commit/4c06658e988f4ced1a7a574ce082a22ef625df56
- https://github.com/ntpsec/gpsd/commit/5581ba196d826a984fbfaf792b7d58535f9911ce
- https://github.com/ntpsec/gpsd
