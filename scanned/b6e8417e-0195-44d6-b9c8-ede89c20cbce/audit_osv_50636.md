# [H] CVE-2020-26950

## Summary
Severity: High
Advisory: CVE-2020-26950
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26950
Type: osv

## Details
In certain circumstances, the MCallGetProperty opcode can be emitted with unmet assumptions resulting in an exploitable use-after-free condition. This vulnerability affects Firefox < 82.0.3, Firefox ESR < 78.4.1, and Thunderbird < 78.4.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1675905
- http://packetstormsecurity.com/files/166175/Firefox-MCallGetProperty-Write-Side-Effects-Use-After-Free.html
