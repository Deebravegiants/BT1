# [H] Grav's Twig processing allowing dangerous PHP functions by default

## Summary
Severity: High
Advisory: GHSA-g8r4-p96j-xfxc
CVE: CVE-2021-29440
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-16
Source: https://github.com/advisories/GHSA-g8r4-p96j-xfxc
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.11

## Details
### Impact

Twig processing of static pages can be enabled in the front matter by any administrative user allowed to create or edit pages. 
As the Twig processor runs unsandboxed, this behavior can be used to gain arbitrary code execution and elevate privileges on the instance.

### Patches

The issue was addressed by preventing dangerous functions from being called in Twig templates. A configuration option has been added to manually allow arbitrary PHP functions (`system.twig.safe_functions`) and filters (`system.twig.safe_filters`). 

Futures major versions of Grav may disable this functionality by default. 

### Workarounds

Blocking access to the `/admin` path from untrusted sources will reduce the probability of exploitation. 

### References

- https://portswigger.net/research/server-side-template-injection
- https://blog.sonarsource.com/grav-cms-code-execution-vulnerabilities

### For more information

If you have any questions or comments about this advisory, you can contact:
  - The original reporters, by sending an email to vulnerability.research [at] sonarsource.com;
  - The maintainers, by opening an issue on this repository.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-g8r4-p96j-xfxc
- https://nvd.nist.gov/vuln/detail/CVE-2021-29440
- https://blog.sonarsource.com/grav-cms-code-execution-vulnerabilities
- https://packagist.org/packages/getgrav/grav
- http://packetstormsecurity.com/files/162987/Grav-CMS-1.7.10-Server-Side-Template-Injection.html
