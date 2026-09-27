# [M] CVE-2023-49347

## Summary
Severity: Medium
Advisory: CVE-2023-49347
Aliases: GHSA-xxfq-fqfp-cpvj
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-49347
Type: osv

## Details
Temporary data passed between application components by Budgie Extras Windows Previews could potentially be viewed or manipulated. The data is stored in a location that is accessible to any user who has local access to the system. Attackers may read private information from windows, present false information to users, or deny access to the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49347.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49347
- https://ubuntu.com/security/notices/USN-6556-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-49347
- https://github.com/UbuntuBudgie/budgie-extras/security/advisories/GHSA-xxfq-fqfp-cpvj
