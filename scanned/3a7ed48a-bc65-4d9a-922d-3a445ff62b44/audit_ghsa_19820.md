# [H] Mesop Class Pollution vulnerability leads to DoS and Jailbreak attacks

## Summary
Severity: High
Advisory: GHSA-f3mf-hm6v-jfhh
CVE: CVE-2025-30358
CWE: CWE-915
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-27
Source: https://github.com/advisories/GHSA-f3mf-hm6v-jfhh
Type: github-advisory

## Affected
- PyPI: `mesop` — affected >=0 <0.14.1

## Details
From @jackfromeast and @superboy-zjc:
We have identified a class pollution vulnerability in Mesop (<= [0.14.0](https://github.com/mesop-dev/mesop/releases/tag/v0.14.0)) application that allows attackers to overwrite global variables and class attributes in certain Mesop modules during runtime. This vulnerability could directly lead to a denial of service (DoS) attack against the server. Additionally, it could also result in other severe consequences given the application's implementation, such as identity confusion, where an attacker could impersonate an assistant or system role within conversations. This impersonation could potentially enable jailbreak attacks when interacting with large language models (LLMs).

Just like the Javascript's prototype pollution, this vulnerability could leave a way for attackers to manipulate the intended data-flow or control-flow of the application at runtime and lead to severe consequnces like RCE when gadgets are available.

## References
- https://github.com/mesop-dev/mesop/security/advisories/GHSA-f3mf-hm6v-jfhh
- https://nvd.nist.gov/vuln/detail/CVE-2025-30358
- https://github.com/mesop-dev/mesop/commit/748e20d4a363d89b841d62213f5b0c6b4bed788f
- https://github.com/mesop-dev/mesop
