# [M] CVE-2020-15646

## Summary
Severity: Medium
Advisory: CVE-2020-15646
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-08
Source: https://osv.dev/vulnerability/CVE-2020-15646
Type: osv

## Details
If an attacker intercepts Thunderbird's initial attempt to perform automatic account setup using the Microsoft Exchange autodiscovery mechanism, and the attacker sends a crafted response, then Thunderbird sends username and password over https to a server controlled by the attacker. This vulnerability affects Thunderbird < 68.10.0.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1606610
