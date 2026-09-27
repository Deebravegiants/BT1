# [C] Remote Code Execution in scratch-vm

## Summary
Severity: Critical
Advisory: GHSA-vc9j-fhvv-8vrf
CVE: CVE-2020-14000
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-vc9j-fhvv-8vrf
Type: github-advisory

## Affected
- npm: `scratch-vm` — affected >=0 <0.2.0-prerelease.20200714185213

## Details
MIT Lifelong Kindergarten Scratch scratch-vm before `0.2.0-prerelease.20200714185213` loads extension URLs from untrusted project.json files with certain `_` characters, resulting in remote code execution because the URL's content is treated as a script and is executed as a worker. The responsible code is `getExtensionIdForOpcode` in serialization/sb3.js. The use of `_` is incompatible with a protection mechanism in older versions, in which URLs were split and consequently deserialization attacks were prevented. 

**NOTE**: the scratch.mit.edu hosted service is not affected because of the lack of worker scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14000
- https://github.com/LLK/scratch-vm/pull/2476
- https://github.com/LLK/scratch-vm/pull/2476/commits/90b9da45f4084958535338d1c4d71a22d6136aab
- https://github.com/LLK/scratch-vm
- https://scratch.mit.edu/discuss/topic/422904/?page=1#post-4223443
