# [H] OS Command Injection in Microweber

## Summary
Severity: High
Advisory: GHSA-vm37-j55j-8655
CVE: CVE-2022-0557
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-vm37-j55j-8655
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.2.11

## Details
Microweber is a content management system with drag and drop. Prior to version 1.2.11, Microweber is vulnerable to OS Command Injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0557
- https://github.com/microweber/microweber/commit/0a7e5f1d81de884861ca677ee1aaac31f188d632
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/660c89af-2de5-41bc-aada-9e4e78142db8
- https://www.exploit-db.com/exploits/50768
- http://packetstormsecurity.com/files/166077/Microweber-1.2.11-Shell-Upload.html
