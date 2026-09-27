# [M] Craft CMS Vulnerable to Authenticated RCE via Twig SSTI - create() function + Symfony Process gadget

## Summary
Severity: Medium
Advisory: GHSA-94rc-cqvm-m4pw
CVE: CVE-2026-28695
CWE: CWE-1336, CWE-22, CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-94rc-cqvm-m4pw
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.8.7 <5.9.0-beta.1
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1

## Details
There is an authenticated admin RCE in Craft CMS 5.8.21 via Server-Side Template Injection using the `create()` Twig function combined with a Symfony Process gadget chain.

This bypasses the fix implemented for CVE-2025-57811 (patched in 5.8.7).

## Required Permissions

- Administrator permissions or access to System Messages utility
- `allowAdminChanges` enabled in production ([against our security recommendations](https://craftcms.com/knowledge-base/securing-craft#set-allowAdminChanges-to-false-in-production))  or access to System Messages utility

## Vulnerability Details
The `create()` Twig function exposes `Craft::createObject()`, which allows instantiation of arbitrary PHP classes with constructor arguments. Combined with the bundled `symfony/process` dependency, this enables RCE.

## Attack Vector
Admin panel → Settings → Entry Types → Title Format field

## Proof of Concept Payload

```
{% set p = create("Symfony\\Component\\Process\\Process", [["id"]])
%}{{ p.mustRun.getOutput }}
```

## Steps to Reproduce
1. Log in as admin
2. Navigate to Settings → Entry Types
3. Edit any entry type’s "Title Format" field
4. Insert the payload above
5. Create/edit an entry of that type
6. Command executes, output appears in entry title

## Impact
- Authenticated Remote Code Execution
- Runs as web server user (root in default Docker setup)
- Full server compromise

## Root Cause
Craft::createObject() allows the instantiation of any class, including
`Symfony\Component\Process\Process`, which executes shell commands.

## Suggested Fix

- Blocklist dangerous classes in createObject() when called from Twig
- Or remove/restrict the create() Twig function
- Or validate class names against an allowlist

## Resources

https://github.com/craftcms/cms/commit/e31e50849ad71638e11ea55fbd1ed90ae8f8f6e0

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-94rc-cqvm-m4pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-28695
- https://github.com/craftcms/cms/commit/e31e50849ad71638e11ea55fbd1ed90ae8f8f6e0
- https://github.com/craftcms/cms
