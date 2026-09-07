# [C] Command Injection in sequenceserver

## Summary
Severity: Critical
Advisory: GHSA-qv32-5wm2-p32h
CVE: CVE-2024-42360
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-13
Source: https://github.com/advisories/GHSA-qv32-5wm2-p32h
Type: github-advisory

## Affected
- RubyGems: `sequenceserver` — affected >=0 <3.1.2

## Details
### Impact

Several HTTP endpoints did not properly sanitize user input and/or query parameters. This could be exploited to inject and run unwanted shell commands

### Patches

Fixed in 3.1.2

### Workarounds

No known workarounds

## References
- https://github.com/wurmlab/sequenceserver/security/advisories/GHSA-qv32-5wm2-p32h
- https://nvd.nist.gov/vuln/detail/CVE-2024-42360
- https://github.com/wurmlab/sequenceserver/commit/457e52709f7f9ed2fceed59b3db564cb50785dba
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sequenceserver/CVE-2024-42360.yml
- https://github.com/wurmlab/sequenceserver
