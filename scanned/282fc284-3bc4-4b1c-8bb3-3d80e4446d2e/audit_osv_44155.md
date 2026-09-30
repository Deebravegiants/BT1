# [C] bestzip before 2.2.6 and 3.0.x before 3.0.2 Argument Injection via Missing Option Delimiter

## Summary
Severity: Critical
Advisory: CVE-2026-80427
Aliases: GHSA-p87m-9567-rgcc
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80427
Type: osv

## Details
bestzip builds the argument list for the system zip utility without separating options from operands. The destination archive path and the caller-supplied source paths are passed to the child process with no -- delimiter between them, so any source entry beginning with a hyphen is interpreted by zip as an option rather than a file name. zip accepts -T to test the finished archive and -TT to name the command used to perform that test, so a source list containing those two entries and a command string causes zip to run that command through a shell once the archive has been written. An application that passes a file name or path it received from an untrusted source into the bestzip API therefore executes a command of the supplier's choosing. Versions 2.2.6 and 3.0.2 add the delimiter.

## References
- https://www.npmjs.com/package/bestzip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80427.json
- https://github.com/nfriedly/node-bestzip/security/advisories/GHSA-p87m-9567-rgcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-80427
- https://www.vulncheck.com/advisories/bestzip-before-2.2.6-and-3.0-x-before-3.0.2-argument-injection-via-missing-option-delimiter
- https://github.com/nfriedly/node-bestzip
