# [C] Remote shell execution vulnerability in image_processing

## Summary
Severity: Critical
Advisory: GHSA-cxf7-qrc5-9446
CVE: CVE-2022-24720
CWE: CWE-20, CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-cxf7-qrc5-9446
Type: github-advisory

## Affected
- RubyGems: `image_processing` — affected >=0 <1.12.2

## Details
### Impact

When using the `#apply` method from image_processing to apply a series of operations that are coming from unsanitized user input, this allows the attacker to execute shell commands:

```rb
ImageProcessing::Vips.apply({ system: "echo EXECUTED" })
#>> EXECUTED
```

This method is called internally by Active Storage variants, so Active Storage is vulnerable as well.

### Patches

The vulnerability has been fixed in version 1.12.2 of image_processing.

### Workarounds

If you're processing based on user input, it's highly recommended that you always sanitize the user input, by allowing only a constrained set of operations. For example:

```rb
operations = params[:operations]
  .map { |operation| [operation[:name], *operation[:value]] }
  .select { |name, *| name.to_s.include? %w[resize_to_limit strip ...] } # sanitization

ImageProcessing::Vips.apply(operations)
```

## References
- https://github.com/janko/image_processing/security/advisories/GHSA-cxf7-qrc5-9446
- https://nvd.nist.gov/vuln/detail/CVE-2022-24720
- https://github.com/janko/image_processing/commit/038e4574e8f4f4b636a62394e09983c71980dada
- https://github.com/janko/image_processing
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/image_processing/CVE-2022-24720.yml
- https://www.debian.org/security/2022/dsa-5310
