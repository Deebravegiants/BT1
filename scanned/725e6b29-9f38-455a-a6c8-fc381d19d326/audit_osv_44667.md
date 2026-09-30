# [C] MOOS-IvP through 24.8.1 alogsplit Command Injection via Input Pathname

## Summary
Severity: Critical
Advisory: CVE-2026-85439
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85439
Type: osv

## Details
MOOS-IvP through 24.8.1 contains a remote code execution vulnerability in alogsplit's SplitHandler::handlePreCheckSplitDir() function that fails to sanitize shell metacharacters in log file pathnames. Attackers can embed shell syntax in log file names or the --dir parameter to execute arbitrary commands with the privileges of the operator running alogsplit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85439.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85439
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-alogsplit-command-injection-via-input-pathname
- https://github.com/moos-ivp/moos-ivp/commit/f684d77d9d6e9e96dbfce46f05988d5a643f2b60
- https://github.com/moos-ivp/moos-ivp/pull/127
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/lib_logutils/SplitHandler.cpp#L608
