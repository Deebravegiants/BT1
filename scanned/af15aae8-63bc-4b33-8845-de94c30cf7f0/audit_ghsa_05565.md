# [M] OctoPrint has Timing Side-Channel Vulnerability in API Key Authentication

## Summary
Severity: Medium
Advisory: GHSA-xg4x-w2j3-57h6
CVE: CVE-2026-23892
CWE: CWE-208
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-xg4x-w2j3-57h6
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.11.6

## Details
### Impact

OctoPrint versions up to and including 1.11.5 are affected by a (theoretical) timing attack vulnerability that allows API key extraction over the network.

Due to using character based comparison that short-circuits on the first mismatched character during API key validation, rather than a cryptographical method with static runtime regardless of the point of mismatch, an attacker with network based access to an affected OctoPrint could extract API keys valid on the instance by measuring the response times of the denied access responses and guess an API key character by character.

### Patches

The vulnerability will be patched in version 1.11.6.

### Workaround

The likelihood of this attack actually working is highly dependent on the network's latency, noise and similar parameters. An actual proof of concept was not achieved so far. Still, as always administrators are advised to not expose their OctoPrint instance on hostile networks, especially not on the public Internet!

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by [Knox Liu](https://github.com/yueyueL).

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-xg4x-w2j3-57h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-23892
- https://github.com/OctoPrint/OctoPrint/commit/249fd80ab01bc4b7dabedff768230a0fb5d01a8c
- https://github.com/OctoPrint/OctoPrint
- https://github.com/OctoPrint/OctoPrint/releases/tag/1.11.6
