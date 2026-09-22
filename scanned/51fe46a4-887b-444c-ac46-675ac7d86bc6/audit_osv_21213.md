# [M] CVE-2021-41168

## Summary
Severity: Medium
Advisory: CVE-2021-41168
Aliases: GHSA-6gvv-9q92-w5f6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-21
Source: https://osv.dev/vulnerability/CVE-2021-41168
Type: osv

## Details
Snudown is a reddit-specific fork of the Sundown Markdown parser used by GitHub, with Python integration added. In affected versions snudown was found to be vulnerable to denial of service attacks to its reference table implementation. References written in markdown ` [reference_name]: https://www.example.com` are inserted into a hash table which was found to have a weak hash function, meaning that an attacker can reliably generate a large number of collisions for it. This makes the hash table vulnerable to a hash-collision DoS attack, a type of algorithmic complexity attack. Further the hash table allowed for duplicate entries resulting in long retrieval times. Proofs of concept and further discussion of the hash collision issue are discussed on the snudown GHSA(https://github.com/reddit/snudown/security/advisories/GHSA-6gvv-9q92-w5f6). Users are advised to update to version 1.7.0.

## References
- https://github.com/reddit/snudown/commit/1ac2c130b210539ee1e5d67a7bac93f9d8007c0e
- https://github.com/reddit/snudown/security/advisories/GHSA-6gvv-9q92-w5f6
