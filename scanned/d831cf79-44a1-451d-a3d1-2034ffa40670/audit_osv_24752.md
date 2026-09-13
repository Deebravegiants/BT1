# [H] ZoneMinder vulnerable to Missing Authorization

## Summary
Severity: High
Advisory: CVE-2023-26035
Aliases: GHSA-72rg-h4vf-29gr
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26035
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application for Linux which supports IP, USB and Analog cameras. Versions prior to 1.36.33 and 1.37.33 are vulnerable to Unauthenticated Remote Code Execution via Missing Authorization. There are no permissions check on the snapshot action, which expects an id to fetch an existing monitor but can be passed an object to create a new one instead. TriggerOn ends up calling shell_exec using the supplied Id. This issue is fixed in This issue is fixed in versions 1.36.33 and 1.37.33.

## References
- http://packetstormsecurity.com/files/175675/ZoneMinder-Snapshots-Command-Injection.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26035.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-72rg-h4vf-29gr
- https://nvd.nist.gov/vuln/detail/CVE-2023-26035
