# [H] Ruby OpenSSL DoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-v6rp-3r3v-hf4p
CVE: CVE-2017-14033
CWE: CWE-119
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v6rp-3r3v-hf4p
Type: github-advisory

## Affected
- RubyGems: `openssl` — affected >=0 <2.0.0

## Details
The decode method in the `OpenSSL::ASN1` module in Ruby before 2.2.8, 2.3.x before 2.3.5, and 2.4.x through 2.4.1 allows attackers to cause a denial of service (interpreter crash) via a crafted string. The `openssl` gem that contains this module is patched in version 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14033
- https://github.com/ruby/openssl/commit/36bf7f403ebb6cefcaa1e7af9d8ec99e6b4bc1ed
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0585
- https://github.com/ruby/openssl
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openssl/CVE-2017-14033.yml
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://security.gentoo.org/glsa/201710-18
- https://web.archive.org/web/20210509153849/http://www.securityfocus.com/bid/100868
- https://web.archive.org/web/20210622181826/http://www.securitytracker.com/id/1042004
- https://web.archive.org/web/20210724095519/http://www.securitytracker.com/id/1039363
- https://www.debian.org/security/2017/dsa-4031
- https://www.ruby-lang.org/en/news/2017/09/14/openssl-asn1-buffer-underrun-cve-2017-14033
- https://www.ruby-lang.org/en/news/2017/09/14/ruby-2-2-8-released
- https://www.ruby-lang.org/en/news/2017/09/14/ruby-2-3-5-released
