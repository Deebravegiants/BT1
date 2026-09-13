# [C] BIT-ruby-2022-28738

## Summary
Severity: Critical
Advisory: BIT-ruby-2022-28738
Aliases: BIT-ruby-min-2022-28738, CVE-2022-28738
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ruby-2022-28738
Type: osv

## Affected
- Bitnami: `ruby` — affected >=3.1.0 <3.1.2

## Details
A double free was found in the Regexp compiler in Ruby 3.x before 3.0.4 and 3.1.x before 3.1.2. If a victim attempts to create a Regexp from untrusted user input, an attacker may be able to write to unexpected memory locations.

## References
- https://hackerone.com/reports/1220911
- https://security-tracker.debian.org/tracker/CVE-2022-28738
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20220624-0002/
- https://www.ruby-lang.org/en/news/2022/04/12/double-free-in-regexp-compilation-cve-2022-28738/
- https://nvd.nist.gov/vuln/detail/CVE-2022-28738
