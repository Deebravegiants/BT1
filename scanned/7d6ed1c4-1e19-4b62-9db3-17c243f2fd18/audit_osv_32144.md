# [C] Command Injection in reNgine

## Summary
Severity: Critical
Advisory: CVE-2025-24962
Aliases: GHSA-cg75-ph7x-5rr9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2025-24962
Type: osv

## Details
reNgine is an automated reconnaissance framework for web applications. In affected versions a user can inject commands via the nmap_cmd parameters. This issue has been addressed in commit `c28e5c8d` and is expected in the next versioned release. Users are advised to filter user input and monitor the project for a new release.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24962.json
- https://github.com/yogeshojha/rengine/security/advisories/GHSA-cg75-ph7x-5rr9
- https://nvd.nist.gov/vuln/detail/CVE-2025-24962
- https://github.com/yogeshojha/rengine/commit/c28e5c8d304478a787811580b4d80b330920ace4
