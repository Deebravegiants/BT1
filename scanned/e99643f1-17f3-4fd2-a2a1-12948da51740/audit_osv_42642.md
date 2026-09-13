# [H] Grav CMS 2.0.7 through 2.0.10 Arbitrary Method Invocation via Blueprint

## Summary
Severity: High
Advisory: CVE-2026-69088
Aliases: GHSA-7pgq-cr25-xvc8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69088
Type: osv

## Details
Grav CMS versions 2.0.7 through 2.0.10 fail to validate fully-qualified static method calls (Class::method) in blueprint dynamic-field directives because Blueprint::isSafeDynamicCall() only applies its dangerous-callable denylist to strings that do not contain '::'. An account with only page-editing rights (admin.pages, not super-admin or admin.pages_twig) can plant a directive in a page's form-field frontmatter that invokes an arbitrary public static PHP method with attacker-controlled arguments. Using built-in gadget methods this allows reading of any server-readable file (disclosed to anonymous visitors of the crafted page) and arbitrary creation/copying of files and directories under the web-server account. Fixed in 2.0.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69088.json
- https://github.com/getgrav/grav/security/advisories/GHSA-7pgq-cr25-xvc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-69088
- https://www.vulncheck.com/advisories/grav-cms-through-arbitrary-method-invocation-via-blueprint
