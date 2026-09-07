# [M] Nokogiri::XML::Schema trusts input by default, exposing risk of XXE vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vr8q-g5c7-m54m
CVE: CVE-2020-26247
CWE: CWE-611
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-12-30
Source: https://github.com/advisories/GHSA-vr8q-g5c7-m54m
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.11.0

## Details
### Severity

Nokogiri maintainers have evaluated this as [__Low Severity__ (CVSS3 2.6)](https://www.first.org/cvss/calculator/3.0#CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:N/A:N).


### Description

In Nokogiri versions <= 1.11.0.rc3, XML Schemas parsed by `Nokogiri::XML::Schema` are **trusted** by default, allowing external resources to be accessed over the network, potentially enabling XXE or SSRF attacks.

This behavior is counter to the security policy followed by Nokogiri maintainers, which is to treat all input as **untrusted** by default whenever possible.

Please note that this security fix was pushed into a new minor version, 1.11.x, rather than a patch release to the 1.10.x branch, because it is a breaking change for some schemas and the risk was assessed to be "Low Severity".


### Affected Versions

Nokogiri `<= 1.10.10` as well as prereleases `1.11.0.rc1`, `1.11.0.rc2`, and `1.11.0.rc3`


### Mitigation

There are no known workarounds for affected versions. Upgrade to Nokogiri `1.11.0.rc4` or later.

If, after upgrading to `1.11.0.rc4` or later, you wish to re-enable network access for resolution of external resources (i.e., return to the previous behavior):

1. Ensure the input is trusted. Do not enable this option for untrusted input.
2. When invoking the `Nokogiri::XML::Schema` constructor, pass as the second parameter an instance of `Nokogiri::XML::ParseOptions` with the `NONET` flag turned off.

So if your previous code was:

``` ruby
# in v1.11.0.rc3 and earlier, this call allows resources to be accessed over the network
# but in v1.11.0.rc4 and later, this call will disallow network access for external resources
schema = Nokogiri::XML::Schema.new(schema)

# in v1.11.0.rc4 and later, the following is equivalent to the code above
# (the second parameter is optional, and this demonstrates its default value)
schema = Nokogiri::XML::Schema.new(schema, Nokogiri::XML::ParseOptions::DEFAULT_SCHEMA)
```

Then you can add the second parameter to indicate that the input is trusted by changing it to:

``` ruby
# in v1.11.0.rc3 and earlier, this would raise an ArgumentError 
# but in v1.11.0.rc4 and later, this allows resources to be accessed over the network
schema = Nokogiri::XML::Schema.new(trusted_schema, Nokogiri::XML::ParseOptions.new.nononet)
```


### References

- [This issue's public advisory](https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-vr8q-g5c7-m54m)
- [Original Hackerone report (private)](https://hackerone.com/reports/747489)
- [OWASP description of XXE attack](https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing)
- [OWASP description of SSRF attack](https://www.owasp.org/index.php/Server_Side_Request_Forgery)


### Credit 

This vulnerability was independently reported by @eric-therond and @gucki.

The Nokogiri maintainers would like to thank [HackerOne](https://hackerone.com/nokogiri) for providing a secure, responsible mechanism for reporting, and for providing their fantastic service to us.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-vr8q-g5c7-m54m
- https://nvd.nist.gov/vuln/detail/CVE-2020-26247
- https://github.com/sparklemotion/nokogiri/commit/9c87439d9afa14a365ff13e73adc809cb2c3d97b
- https://hackerone.com/reports/747489
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2020-26247.yml
- https://github.com/sparklemotion/nokogiri
- https://github.com/sparklemotion/nokogiri/blob/main/CHANGELOG.md#v1110--2021-01-03
- https://github.com/sparklemotion/nokogiri/releases/tag/v1.11.0.rc4
- https://lists.debian.org/debian-lts-announce/2021/06/msg00007.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00018.html
- https://rubygems.org/gems/nokogiri
- https://security.gentoo.org/glsa/202208-29
