# [H] sviehb/jefferson vulnerable to path traversal

## Summary
Severity: High
Advisory: GHSA-7jrw-p8jc-v6qw
CVE: CVE-2022-4885
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-7jrw-p8jc-v6qw
Type: github-advisory

## Affected
- PyPI: `jefferson` — affected >=0 <0.4

## Details
A vulnerability has been found in the sviehb/jefferson JFFS2 filesystem extraction tool. This vulnerability affects unknown code of the file `src/scripts/jefferson`. The manipulation leads to path traversal. The attack can be initiated remotely. Upgrading to version 0.4 is able to address this issue as it includes https://github.com/sviehb/jefferson/commit/53b3f2fc34af0bb32afbcee29d18213e61471d87.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4885
- https://github.com/sviehb/jefferson/pull/36
- https://github.com/sviehb/jefferson/commit/53b3f2fc34af0bb32afbcee29d18213e61471d87
- https://github.com/sviehb/jefferson
- https://github.com/sviehb/jefferson/releases/tag/v0.4
- https://vuldb.com/?ctiid.218020
- https://vuldb.com/?id.218020
