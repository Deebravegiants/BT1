# [H] CVE-2019-1010023

## Summary
Severity: High
Advisory: CVE-2019-1010023
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010023
Type: osv

## Details
GNU Libc current is affected by: Re-mapping current loaded library with malicious ELF file. The impact is: In worst case attacker may evaluate privileges. The component is: libld. The attack vector is: Attacker sends 2 ELF files to victim and asks to run ldd on it. ldd execute code. NOTE: Upstream comments indicate "this is being treated as a non-security bug and no real threat.

## References
- https://security-tracker.debian.org/tracker/CVE-2019-1010023
- https://support.f5.com/csp/article/K11932200?utm_source=f5support&amp%3Butm_medium=RSS
- https://ubuntu.com/security/CVE-2019-1010023
- http://www.securityfocus.com/bid/109167
- https://sourceware.org/bugzilla/show_bug.cgi?id=22851
