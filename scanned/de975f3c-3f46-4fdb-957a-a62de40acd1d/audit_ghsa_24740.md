# [H] Denial of Service Vulnerability in Rack Multipart Parsing

## Summary
Severity: High
Advisory: GHSA-hxqx-xwvh-44m2
CVE: CVE-2022-30122
CWE: CWE-1333, CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-27
Source: https://github.com/advisories/GHSA-hxqx-xwvh-44m2
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=1.2 <2.0.9.1
- RubyGems: `rack` — affected >=2.1 <2.1.4.1
- RubyGems: `rack` — affected >=2.2 <2.2.3.1

## Details
There is a possible denial of service vulnerability in the multipart parsing component of Rack.  This vulnerability has been assigned the CVE identifier CVE-2022-30122.

Versions Affected:  >= 1.2
Not affected:       < 1.2
Fixed Versions:     2.0.9.1, 2.1.4.1, 2.2.3.1

## Impact
Carefully crafted multipart POST requests can cause Rack's multipart parser to take much longer than expected, leading to a possible denial of service vulnerability.

Impacted code will use Rack's multipart parser to parse multipart posts.  This includes directly using the multipart parser like this:

```
params = Rack::Multipart.parse_multipart(env)
```

But it also includes reading POST data from a Rack request object like this:

```
p request.POST # read POST data
p request.params # reads both query params and POST data
```

All users running an affected release should either upgrade or use one of the workarounds immediately.

## Workarounds
There are no feasible workarounds for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30122
- https://discuss.rubyonrails.org/t/cve-2022-30122-denial-of-service-vulnerability-in-rack-multipart-parsing/80729
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2022-30122.yml
- https://groups.google.com/g/ruby-security-ann/c/L2Axto442qk
- https://security.gentoo.org/glsa/202310-18
- https://security.netapp.com/advisory/ntap-20231208-0012
- https://www.debian.org/security/2023/dsa-5530
