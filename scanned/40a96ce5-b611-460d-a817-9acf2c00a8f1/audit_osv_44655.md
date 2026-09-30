# [C] MOOS essential-moos through 10.0.1 pAntler Remote Code Execution via Unauthenticated MISSION_FILE

## Summary
Severity: Critical
Advisory: CVE-2026-85427
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85427
Type: osv

## Details
MOOS essential-moos pAntler through 10.0.1 contains a remote code execution vulnerability that allows unauthenticated attackers to execute arbitrary programs by publishing a crafted MISSION_FILE message to the MOOSDB. Attackers can publish a mission file containing malicious Run entries that pAntler parses and executes via execvp() without authentication validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85427.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85427
- https://www.vulncheck.com/advisories/moos-essential-moos-through-10.0.1-pantler-remote-code-execution-via-unauthenticated-mission-file
- https://github.com/themoos/essential-moos/commit/e219f26710927f9c155a6b0dc11e3bd5f3da6730
- https://github.com/themoos/essential-moos/pull/17
- https://github.com/themoos/essential-moos
- https://github.com/themoos/essential-moos/blob/b897ea86dba8b61412dc48ac0cfb5ff34cdaf5f6/Essentials/pAntler/Antler.cpp#L95
