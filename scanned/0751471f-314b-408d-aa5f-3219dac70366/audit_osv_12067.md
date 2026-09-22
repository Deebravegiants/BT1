# [C] CVE-2018-1000884

## Summary
Severity: Critical
Advisory: CVE-2018-1000884
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000884
Type: osv

## Details
Vesta CP version Prior to commit f6f6f9cfbbf2979e301956d1c6ab5c44386822c0 -- any release prior to 0.9.8-18 contains a CWE-208 / Information Exposure Through Timing Discrepancy vulnerability in Password reset code -- web/reset/index.php, line 51 that can result in Possible to determine password reset codes, attacker is able to change administrator password. This attack appear to be exploitable via Unauthenticated network connectivity. This vulnerability appears to have been fixed in After commit f6f6f9cfbbf2979e301956d1c6ab5c44386822c0 -- release version 0.9.8-19.

## References
- https://github.com/serghey-rodin/vesta/commit/5f68c1b634abec2d5a4f83156bfd223d3a792f77#diff-4d7863e8c24a5e6102073acc2fb0f227
