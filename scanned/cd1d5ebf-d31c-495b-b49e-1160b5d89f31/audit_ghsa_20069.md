# [C] Nadesiko3 OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-m8r5-7wf4-63mw
CVE: CVE-2022-41642
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-m8r5-7wf4-63mw
Type: github-advisory

## Affected
- npm: `nadesiko3` — affected >=0 <3.3.69

## Details
OS command injection vulnerability in Nadesiko3 (PC Version) v3.3.68 and earlier allows a remote attacker to execute an arbitrary OS command when processing compression and decompression on the product.

Release notes for versions 3.3.62 and 3.3.69 both link to patches for this particular issue. The [JPCERT/CC](https://jvn.jp/en/jp/JVN56968681/index.html) advisory lists versions 3.3.68 and prior as vulnerable, and the most recent patch for this issue is tagged with version 3.3.69.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41642
- https://github.com/kujirahand/nadesiko3/issues/1325
- https://github.com/kujirahand/nadesiko3/issues/1347
- https://github.com/kujirahand/nadesiko3/commit/124871c064cfc65cdcd83205637e84fc246c76df
- https://github.com/kujirahand/nadesiko3/commit/56ccfb2f9cceaec83e6a9d3024c3ba8c54ebe1a4
- https://github.com/kujirahand/nadesiko3/commit/61a70792752a75b7f71df214e98a236721ea3fa6
- https://github.com/kujirahand/nadesiko3
- https://github.com/kujirahand/nadesiko3/releases/tag/3.3.62
- https://github.com/kujirahand/nadesiko3/releases/tag/3.3.69
- https://jvn.jp/en/jp/JVN56968681/index.html
