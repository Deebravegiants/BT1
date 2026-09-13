# [H] Craft CMS: Authenticated RCE through Twig sandbox escape

## Summary
Severity: High
Advisory: GHSA-f5wm-88jv-g5hx
CVE: CVE-2026-72781
CWE: CWE-693
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-f5wm-88jv-g5hx
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.7
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18.3

## Details
The Twig sandbox mechanism in Craft CMS is configured to allow dangerous functionality from the Yii framework, leading to authenticated RCE in a manner similar to previously disclosed vulnerabilities.

The Twig sandbox in Craft CMS works by implementing Twig's `SecurityPolicyInterface`. The resulting `SecurityPolicy` class implements the `checkMethodAllowed` and `checkPropertyAllowed` methods of the interface. The implementations compare whether the called method or property is in a configured allowlist or is marked with the `AllowedInSandbox` attribute.

Additionally, `SecurityPolicy` allows the allowlisting of whole classes, which is shorthand for allowing all methods and properties of that class to be called. Both the allowlists for tags, filters, variables, methods, properties, and classes, as well as the `AllowedInSandbox` attribute mechanism, are preconfigured by Craft CMS to allow user-defined templates to use core functionality unimpeded. Additionally, Craft CMS project developers can add more to the allowlists or mark their custom methods and so on as safe with `AllowedInSandbox`.

The `SecurityPolicy` class's allowlisting mechanism is potentially dangerous, as it allows all methods and properties on an object of the allowed class. This means that the checked object can be a subclass and be allowed. And it means that the allowed methods and properties can be defined on any class of the class hierarchy of the object, which does not have to be the allowed class itself.


Craft CMS uses the `AllowedInSandbox` attribute to mark the `ElementInterface` as safe. The `Element` class implements this interface and is the base class for many relevant model classes in Craft CMS, like `Entry`, `User`, `Asset` and so on. Additionally, `Element` extends the `craft\base\Component` class. Going up the class hierarchy of `craft\base\Component`, eventually the class `yii\base\Component` is reached, which is located in the Yii framework used by CraftCMS. `yii\base\Component` is known to contain a dangerous arbitrary function call gadget which leads to previously disclosed RCE vulnerabilities in Craft CMS (GHSA-255j-qw47-wjh5, GHSA-2fph-6v5w-89hh, GHSA-7jx7-3846-m7w7, GHSA-qrgm-p9w5-rrfw). Due to lax class allowlisting, this function-call gadget is allowed in the Twig sandbox. This allows sandboxed Twig templates to use known payloads based on the function-call gadget to achieve RCE.

## Impact

An authenticated attacker with permission to access the control panel can render a malicious Twig template and gain RCE, even if the Twig sandbox is enabled through `enableTwigSandbox()`.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-f5wm-88jv-g5hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-72781
- https://github.com/craftcms/cms/commit/0b8be1556be4e030578ec779c3e17ffe2e69d7db
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.18.3
- https://github.com/craftcms/cms/releases/tag/5.10.7
- https://www.vulncheck.com/advisories/craft-cms-rc1-before-remote-code-execution-via-twig-sandbox-escape
