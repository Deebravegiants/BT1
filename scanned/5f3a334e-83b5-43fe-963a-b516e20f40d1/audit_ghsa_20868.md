# [H] arr-pm vulnerable to arbitrary shell execution when extracting or listing files contained in a malicious rpm.

## Summary
Severity: High
Advisory: GHSA-88cv-mj24-8w3q
CVE: CVE-2022-39224
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-88cv-mj24-8w3q
Type: github-advisory

## Affected
- RubyGems: `arr-pm` — affected >=0 <0.0.12

## Details
### Impact

Arbitrary shell execution is possible when using RPM::File#files and RPM::File#extract if the RPM contains a malicious "payload compressor" field.

This vulnerability impacts the `extract` and `files` methods of the `RPM::File` class in the affected versions of this library.

### Patches

Version 0.0.12 is available with a fix for these issues.

### Workarounds

When using an affected version of this library (arr-pm), ensure any RPMs being processed contain valid/known payload compressor values. Such values include: gzip, bzip2, xz, zstd, and lzma.

You can check the payload compressor field in an rpm by using the rpm command line tool. For example:

```
% rpm -qp example-1.0-1.x86_64.rpm --qf "%{PAYLOADCOMPRESSOR}\n"
gzip
```

### Impact on known dependent projects

This library is used by [fpm](https://github.com/jordansissel/fpm). The vulnerability may impact fpm only when using the flag `-s rpm` or `--input-type rpm` to convert a malicious rpm to another format. It does not impact creating rpms.

### References

* https://github.com/jordansissel/ruby-arr-pm/pull/14
* https://github.com/jordansissel/ruby-arr-pm/pull/15

### Credit

Thanks to @joernchen for reporting this problem and contributing to the resolution :)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [the arr-pm issue tracker](https://github.com/jordansissel/ruby-arr-pm/)

## References
- https://github.com/jordansissel/ruby-arr-pm/security/advisories/GHSA-88cv-mj24-8w3q
- https://nvd.nist.gov/vuln/detail/CVE-2022-39224
- https://github.com/jordansissel/ruby-arr-pm/pull/14
- https://github.com/jordansissel/ruby-arr-pm/pull/15
- https://github.com/jordansissel/ruby-arr-pm
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/arr-pm/CVE-2022-39224.yml
