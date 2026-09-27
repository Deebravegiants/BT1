# [H] Dancer2 versions through 2.1.0 for Perl generate insecure session ids when required CSPRNG modules are unavailable

## Summary
Severity: High
Advisory: CVE-2026-13577
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-13577
Type: osv

## Details
Dancer2 versions through 2.1.0 for Perl generate insecure session ids when required CSPRNG modules are unavailable.

Dancer2::Core::Role::SessionFactory::generate_id silently falls back to a built-in rand-derived session id unless both Math::Random::ISAAC::XS and Crypt::URandom are available.

The fallback session id is generated from a SHA-1 hash of a call to the built-in rand function, the absolute path of the Dancer2::Core::Role::SessionFactory module, an internal counter, the process id, the module instance memory address, and a shuffled string of characters (using the List::Util::shuffle function, which also uses the built-in rand function).

These are all low-entropy and easily guessed sources.

The built-in rand() function is seeded with 32-bits and considered unsuitable for security applications.

Predictable session ids could allow an attacker to gain access to systems.

## References
- https://cpan.org/modules
- https://github.com/PerlDancer/Dancer2/blob/v2.1.0/lib/Dancer2/Core/Role/SessionFactory.pm#L142
- https://www.cve.org/CVERecord?id=CVE-2026-5080
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13577.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13577
- https://github.com/PerlDancer/Dancer2
