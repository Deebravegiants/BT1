# [H] rubyipmi is vulnerable to OS Command Injection through malicious usernames

## Summary
Severity: High
Advisory: GHSA-hfcp-477w-3wjw
CVE: CVE-2026-0980
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-hfcp-477w-3wjw
Type: github-advisory

## Affected
- RubyGems: `rubyipmi` — affected >=0 <0.13.0

## Details
A flaw was found in rubyipmi, a gem used in the Baseboard Management Controller (BMC) component of Red Hat Satellite. An authenticated attacker with host creation or update permissions could exploit this vulnerability by crafting a malicious username for the BMC interface. This could lead to remote code execution (RCE) on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0980
- https://github.com/logicminds/rubyipmi/commit/252503a7b4dca68388165883b0322024e344a215
- https://access.redhat.com/errata/RHSA-2026:5968
- https://access.redhat.com/errata/RHSA-2026:5970
- https://access.redhat.com/errata/RHSA-2026:5971
- https://access.redhat.com/security/cve/CVE-2026-0980
- https://bugzilla.redhat.com/show_bug.cgi?id=2429874
- https://github.com/logicminds/rubyipmi
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubyipmi/CVE-2026-0980.yml
