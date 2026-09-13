# [M] tqdm CLI arguments injection attack

## Summary
Severity: Medium
Advisory: CVE-2024-34062
Aliases: GHSA-g7vv-2v7x-gj9p, PYSEC-2026-1976
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2024-34062
Type: osv

## Details
tqdm is an open source progress bar for Python and CLI. Any optional non-boolean CLI arguments (e.g. `--delim`, `--buf-size`, `--manpath`) are passed through python's `eval`, allowing arbitrary code execution. This issue is only locally exploitable and had been addressed in release version 4.66.3. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PA3GIGHPWAHCTT4UF57LTPZGWHAX3GW6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QRECVQCCESHBS3UJOWNXQUIX725TKNY6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VA337CYUS4SLRFV2P6MX6MZ2LKFURKJC/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34062.json
- https://github.com/tqdm/tqdm/security/advisories/GHSA-g7vv-2v7x-gj9p
- https://nvd.nist.gov/vuln/detail/CVE-2024-34062
- https://github.com/tqdm/tqdm/commit/4e613f84ed2ae029559f539464df83fa91feb316
