# [H] Anonymous cache poisoning via XHR requests in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2024-47773
Aliases: CVE-2024-47773, GHSA-58vv-9j8h-hw2v
Ecosystem: Bitnami
Published: 2024-10-11
Source: https://osv.dev/vulnerability/BIT-discourse-2024-47773
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.3.2

## Details
Discourse is an open source platform for community discussion. An attacker can make several XHR requests until the cache is poisoned with a response without any preloaded data. This issue only affects anonymous visitors of the site. This problem has been patched in the latest version of Discourse. Users are advised to upgrade. Users unable to upgrade should disable anonymous cache by setting the `DISCOURSE_DISABLE_ANON_CACHE` environment variable to a non-empty value.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-58vv-9j8h-hw2v
- https://nvd.nist.gov/vuln/detail/CVE-2024-47773
