# [H] Command Injection Vulnerability in Mechanize

## Summary
Severity: High
Advisory: GHSA-qrqm-fpv6-6r8g
CVE: CVE-2021-21289
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-02-02
Source: https://github.com/advisories/GHSA-qrqm-fpv6-6r8g
Type: github-advisory

## Affected
- RubyGems: `mechanize` — affected >=2.0.0 <2.7.7

## Details
This security advisory has been created for public disclosure of a Command Injection vulnerability that was responsibly reported by @kyoshidajp (Katsuhiko YOSHIDA).

### Impact

Mechanize `>= v2.0`, `< v2.7.7` allows for OS commands to be injected using several classes' methods which implicitly use Ruby's `Kernel.open` method. Exploitation is possible only if untrusted input is used as a local filename and passed to any of these calls:

- `Mechanize::CookieJar#load`: since v2.0 (see 208e3ed)
- `Mechanize::CookieJar#save_as`: since v2.0 (see 5b776a4)
- `Mechanize#download`: since v2.2 (see dc91667)
- `Mechanize::Download#save` and `#save!` since v2.1 (see 98b2f51, bd62ff0)
- `Mechanize::File#save` and `#save_as`: since v2.1 (see 2bf7519)
- `Mechanize::FileResponse#read_body`: since v2.0 (see 01039f5)


### Patches

These vulnerabilities are patched in Mechanize v2.7.7.


### Workarounds

No workarounds are available. We recommend upgrading to v2.7.7 or later.


### References

See https://docs.rubocop.org/rubocop/cops_security.html#securityopen for background on why `Kernel.open` should not be used with untrusted input.


### For more information

If you have any questions or comments about this advisory, please open an issue in [sparklemotion/mechanize](https://github.com/sparklemotion/mechanize/issues/new).

## References
- https://github.com/sparklemotion/mechanize/security/advisories/GHSA-qrqm-fpv6-6r8g
- https://nvd.nist.gov/vuln/detail/CVE-2021-21289
- https://github.com/sparklemotion/mechanize/commit/66a6a1bfa653a5f13274a396a5e5441238656aa0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mechanize/CVE-2021-21289.yml
- https://github.com/sparklemotion/mechanize
- https://github.com/sparklemotion/mechanize/releases/tag/v2.7.7
- https://lists.debian.org/debian-lts-announce/2021/02/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LBVVJUL4P4KCJH4IQTHFZ4ATXY7XXZPV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YNFZ7ROYS6V4J5L5PRAJUG2AWC7VXR2V
- https://rubygems.org/gems/mechanize
- https://security.gentoo.org/glsa/202107-17
