# [C] Mojolicious::Plugin::CaptchaPNG version 1.05 for Perl uses a weak random number source for generating the captcha text

## Summary
Severity: Critical
Advisory: CVE-2025-40916
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-40916
Type: osv

## Details
Mojolicious::Plugin::CaptchaPNG version 1.05 for Perl uses a weak random number source for generating the captcha.

That version uses the built-in rand() function for generating the captcha text as well as image noise, which is insecure.

## References
- https://cpan.org/modules
- https://metacpan.org/pod/perlfunc#rand
- https://metacpan.org/release/GRYPHON/Mojolicious-Plugin-CaptchaPNG-1.04/diff/GRYPHON/Mojolicious-Plugin-CaptchaPNG-1.05/lib/Mojolicious/Plugin/CaptchaPNG.pm
- https://metacpan.org/release/GRYPHON/Mojolicious-Plugin-CaptchaPNG-1.06/changes
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40916.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40916
- https://github.com/gryphonshafer/Mojo-Plugin-CaptchaPNG
