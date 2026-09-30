# [M] Comrak vulnerable to quadratic runtime issues when parsing Markdown (GHSL-2023-047)

## Summary
Severity: Medium
Advisory: GHSA-8hqf-xjwp-p67v
CVE: CVE-2023-28626
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-03-28
Source: https://github.com/advisories/GHSA-8hqf-xjwp-p67v
Type: github-advisory

## Affected
- crates.io: `comrak` — affected >=0 <0.17.0

## Details
### Impact
A range of quadratic parsing issues from `cmark`/`cmark-gfm` are also present in Comrak. These can be used to craft denial-of-service attacks on services that use Comrak to parse Markdown.

### Patches
0.17.0 contains fixes to known quadratic parsing issues.

### Workarounds

n/a

### References

* https://github.com/commonmark/cmark/issues/255
* https://github.com/commonmark/cmark/issues/389
* https://github.com/commonmark/cmark/issues/373
* https://github.com/commonmark/cmark/issues/299
* https://github.com/commonmark/cmark/issues/388
* https://github.com/commonmark/cmark/issues/284
* https://github.com/commonmark/cmark/issues/218
* https://github.com/commonmark/cmark/pull/232
* https://github.com/github/cmark-gfm/blob/c32ef78bae851cb83b7ad52d0fbff880acdcd44a/test/pathological_tests.py#L63-L65
* https://github.com/github/cmark-gfm/blob/c32ef78bae851cb83b7ad52d0fbff880acdcd44a/test/pathological_tests.py#L87-L89

## References
- https://github.com/kivikakk/comrak/security/advisories/GHSA-8hqf-xjwp-p67v
- https://nvd.nist.gov/vuln/detail/CVE-2023-28626
- https://github.com/commonmark/cmark/issues/389
- https://github.com/commonmark/cmark/issues/388
- https://github.com/commonmark/cmark/issues/373
- https://github.com/commonmark/cmark/issues/299
- https://github.com/commonmark/cmark/issues/284
- https://github.com/commonmark/cmark/issues/255
- https://github.com/commonmark/cmark/issues/218
- https://github.com/commonmark/cmark/pull/232
- https://github.com/kivikakk/comrak/commit/ce795b7f471b01589f842dc09af38b025701178d
- https://github.com/github/cmark-gfm/blob/c32ef78bae851cb83b7ad52d0fbff880acdcd44a/test/pathological_tests.py#L63-L65
- https://github.com/github/cmark-gfm/blob/c32ef78bae851cb83b7ad52d0fbff880acdcd44a/test/pathological_tests.py#L87-L89
- https://github.com/kivikakk/comrak
- https://github.com/kivikakk/comrak/releases/tag/0.17.0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OUYME2VA555X6567H7ORIJQFN4BVGT6N
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PTWZWCT7KCX2KTXTLPUYZ3EHOONG4X46
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VQ3UBC7LE4VPCMZBTADIBL353CH7CPVV
