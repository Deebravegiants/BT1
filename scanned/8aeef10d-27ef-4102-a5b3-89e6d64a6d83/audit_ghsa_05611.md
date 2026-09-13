# [M] tarteaucitron.js has Regular Expression Denial of Service (ReDoS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q5f6-qxm2-mcqm
CVE: CVE-2026-22809
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-q5f6-qxm2-mcqm
Type: github-advisory

## Affected
- npm: `tarteaucitronjs` — affected >=0 <1.29.0

## Details
## Summary

A potential Regular Expression Denial of Service (ReDoS) vulnerability was identified in tarteaucitron.js in the handling of the `issuu_id` parameter. 

## Details

The issue was caused by the use of insufficiently constrained regular expressions applied to attacker-controlled input:

    if (issuu_id.match(/\d+\/\d+/)) {
        issuu_embed = '#' + issuu_id;
    } else if (issuu_id.match(/d=(.*)&u=(.*)/)) {
        issuu_embed = '?' + issuu_id;
    }

These expressions are not anchored and rely on greedy patterns (`.*`). When evaluated against specially crafted input, they may cause excessive backtracking, leading to high CPU consumption and potential denial of service.

## Impact

An attacker able to control the `issuu_id` parameter could exploit this vulnerability to degrade performance or cause temporary service unavailability through CPU exhaustion.

No confidentiality or integrity impact was identified.

## Fix https://github.com/AmauriC/tarteaucitron.js/commit/f0bbdac2fdf3cd24a325fc0928c0d34abf1b7b52

The logic was simplified and hardened by removing ambiguous regular expressions and enforcing strict input validation:

    if (issuu_id.match(/^\d+\/\d+$/)) {
        issuu_embed = '#' + issuu_id;
    } else {
        issuu_embed = '?' + issuu_id;
    }

This change eliminates the risk of catastrophic backtracking and prevents ReDoS conditions.

Additionally, code related to the legacy "Alexa Rank" service was removed. This service, historically provided by Alexa.com via browser toolbars and popularity rankings, has been deprecated for several years and is no longer operational. The Alexa domain is now exclusively associated with the Amazon voice assistant, and the original ranking service has been permanently discontinued.

## References
- https://github.com/AmauriC/tarteaucitron.js/security/advisories/GHSA-q5f6-qxm2-mcqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-22809
- https://github.com/AmauriC/tarteaucitron.js/commit/f0bbdac2fdf3cd24a325fc0928c0d34abf1b7b52
- https://github.com/AmauriC/tarteaucitron.js
