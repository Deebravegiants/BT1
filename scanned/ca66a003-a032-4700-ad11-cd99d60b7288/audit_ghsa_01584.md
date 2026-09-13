# [M] Possible timing attack in derivation_endpoint

## Summary
Severity: Medium
Advisory: GHSA-5jjv-x4fq-qjwp
CVE: CVE-2020-15237
CWE: CWE-203, CWE-208
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-10-05
Source: https://github.com/advisories/GHSA-5jjv-x4fq-qjwp
Type: github-advisory

## Affected
- RubyGems: `shrine` — affected >=0 <3.3.0

## Details
### Impact

When using the `derivation_endpoint` plugin, it's possible for the attacker to use a timing attack to guess the signature of the derivation URL.

### Patches

The problem has been fixed by comparing sent and calculated signature in constant time, using `Rack::Utils.secure_compare`. Users using the `derivation_endpoint` plugin are urged to upgrade to Shrine 3.3.0 or greater.

### Workarounds

Users of older Shrine versions can apply the following monkey-patch after loading the `derivation_endpoint` plugin:

```rb
class Shrine
  class UrlSigner
    def verify_signature(string, signature)
      if signature.nil?
        fail InvalidSignature, "missing \"signature\" param"
      elsif !Rack::Utils.secure_compare(signature, generate_signature(string))
        fail InvalidSignature, "provided signature does not match the calculated signature"
      end
    end
  end
end
```

### References

You can read more about timing attacks [here](https://en.wikipedia.org/wiki/Timing_attack).

## References
- https://github.com/shrinerb/shrine/security/advisories/GHSA-5jjv-x4fq-qjwp
- https://nvd.nist.gov/vuln/detail/CVE-2020-15237
- https://github.com/shrinerb/shrine/commit/1b27090ce31543bf39f186c20ea47c8250fca2f0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/shrine/CVE-2020-15237.yml
- https://github.com/shrinerb/shrine
