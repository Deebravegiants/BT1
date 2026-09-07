# [M] Algolia Search & Discovery for Magento 2 Has Untrusted Data Handling

## Summary
Severity: Medium
Advisory: GHSA-595p-g7xc-c333
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-595p-g7xc-c333
Type: github-advisory

## Affected
- Packagist: `algolia/algoliasearch-magento-2` — affected >=3.17.0-beta.1 <3.17.2
- Packagist: `algolia/algoliasearch-magento-2` — affected >=0 <3.16.2

## Details
### Impact

Versions of the Algolia Search & Discovery extension for Magento 2 prior to **3.17.2** and **3.16.2** contain a vulnerability where data read from the database was treated as a trusted source during job execution.

If an attacker is able to modify records used by the extension’s indexing queue, this could result in **arbitrary PHP code execution** when the affected job is processed.

Exploitation requires the ability to write malicious data to the Magento database and for the indexing queue to be enabled.

---

### Patches

This vulnerability has been fixed in the following versions:

- **3.17.2**
- **3.16.2**

Merchants should upgrade to a supported patched version immediately.

Versions outside the supported maintenance window do **not** receive security updates and remain vulnerable.

---

### Workarounds

Upgrading to a patched version is the only recommended remediation.

If an immediate upgrade is not possible, the following temporary risk mitigations may reduce exposure:

- Disable the Algolia indexing queue to prevent queued jobs from being executed.
- Restrict job execution logic to an explicit allowlist of permitted operations.
- Review the contents of the `algoliasearch_queue` table for unexpected or unrecognized entries.
- If queue archiving is enabled, review historical records in `algoliasearch_queue_archive`.

These mitigations are provided as guidance only and do not replace upgrading to a patched version.

---

### References

- Algolia Search & Discovery for Magento 2 releases:
  - [3.16.2](https://github.com/algolia/algoliasearch-magento-2/releases/tag/3.16.2)
  - [3.17.2](https://github.com/algolia/algoliasearch-magento-2/releases/tag/3.17.2)

## References
- https://github.com/algolia/algoliasearch-magento-2/security/advisories/GHSA-595p-g7xc-c333
- https://github.com/algolia/algoliasearch-magento-2
- https://github.com/algolia/algoliasearch-magento-2/releases/tag/3.16.2
- https://github.com/algolia/algoliasearch-magento-2/releases/tag/3.17.2
