# [C] CVE-2019-10747

## Summary
Severity: Critical
Advisory: CVE-2019-10747
Aliases: GHSA-4g88-fppr-53pp
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-23
Source: https://osv.dev/vulnerability/CVE-2019-10747
Type: osv

## Details
set-value is vulnerable to Prototype Pollution in versions lower than 3.0.1. The function mixin-deep could be tricked into adding or modifying properties of Object.prototype using any of the constructor, prototype and _proto_ payloads.

## References
- https://lists.apache.org/thread.html/b46f35559c4a97cf74d2dd7fe5a48f8abf2ff37f879083920af9b292%40%3Cdev.drat.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3EJ36KV6MXQPUYTFCCTDY54E5Y7QP3AV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E3HNLQZQINMZK6GYB2UTKK4VU7WBV2OT/
- https://snyk.io/vuln/SNYK-JS-SETVALUE-450213
