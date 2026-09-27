# [H] Tie::Hash::Regex versions before 2.0.0 for Perl will throw an exception on unparseable lookup keys

## Summary
Severity: High
Advisory: CVE-2026-77781
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77781
Type: osv

## Details
Tie::Hash::Regex versions before 2.0.0 for Perl will throw an exception on unparseable lookup keys.

The FETCH, EXISTS and DELETE methods throw an exception when on malformed regular expressions.

Each method falls back to a regex match when the key is not already stored in the hash, compiling the caller's key with a bare qr// and no eval guard. A key that is not a valid regular expression pattern, such as a single unmatched bracket, dies.

An application that looks up externally supplied strings in a tied hash will die on an invalid key.

## References
- http://www.openwall.com/lists/oss-security/2026/08/22/2
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77781.json
- https://metacpan.org/release/DAVECROSS/Tie-Hash-Regex-2.0.0/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-77781
- https://github.com/davorg-cpan/tie-hash-regex/commit/4239732cb76233543e2ded8ff5e0f238af152e0c.patch
- https://github.com/davorg-cpan/tie-hash-regex
