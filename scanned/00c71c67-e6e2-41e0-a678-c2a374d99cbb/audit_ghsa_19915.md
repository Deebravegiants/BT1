# [C] Aim External Control of File Name or Path vulnerability

## Summary
Severity: Critical
Advisory: GHSA-75px-35p4-qq6h
CVE: CVE-2024-6829
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-75px-35p4-qq6h
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
A vulnerability in aimhubio/aim version 3.19.3 allows an attacker to exploit the `tarfile.extractall()` function to extract the contents of a maliciously crafted tarfile to arbitrary locations on the host server. The attacker can control `repo.path` and `run_hash` to bypass directory existence checks and extract files to unintended locations, potentially overwriting critical files. This can lead to arbitrary data being written to arbitrary locations on the remote tracking server, which could be used for further attacks such as writing a new SSH key to the target server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6829
- https://github.com/aimhubio/aim
- https://huntr.com/bounties/7c97065c-1b63-4982-82c1-8038be0ed570
