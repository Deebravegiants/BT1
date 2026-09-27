# [M] vrana/adminer vulnerable to SSRF by connecting to privileged ports

## Summary
Severity: Medium
Advisory: GHSA-43f8-p5w3-5m25
CVE: CVE-2018-7667
CWE: CWE-918
Ecosystem: Packagist
Published: 2021-02-11
Source: https://github.com/advisories/GHSA-43f8-p5w3-5m25
Type: github-advisory

## Affected
- Packagist: `vrana/adminer` — affected >=0 <4.7.8

## Details
### Impact
All users are affected.

### Patches
* Unsuccessfully patched by 0fae40fb, included in version [4.4.0](https://github.com/vrana/adminer/releases/tag/v4.4.0).
* Patched by 35bfaa75, included in version [4.7.8](https://github.com/vrana/adminer/releases/tag/v4.7.8).

### Workarounds
Protect access to Adminer also by other means, e.g. by HTTP password, IP address limiting or by OTP [plugin](https://www.adminer.org/plugins/).

### References
* http://hyp3rlinx.altervista.org/advisories/ADMINER-UNAUTHENTICATED-SERVER-SIDE-REQUEST-FORGERY.txt
* https://sourceforge.net/p/adminer/bugs-and-features/769/
* https://gusralph.info/adminer-ssrf-bypass-cve-2018-7667/ (CVE-2020-28654)

### For more information
If you have any questions or comments about this advisory:
* Comment at 35bfaa75.

## References
- https://github.com/vrana/adminer/security/advisories/GHSA-43f8-p5w3-5m25
- https://github.com/vrana/adminer/commit/35bfaa75
- https://gusralph.info/adminer-ssrf-bypass-cve-2018-7667
- https://sourceforge.net/p/adminer/bugs-and-features/769
- http://hyp3rlinx.altervista.org/advisories/ADMINER-UNAUTHENTICATED-SERVER-SIDE-REQUEST-FORGERY.txt
