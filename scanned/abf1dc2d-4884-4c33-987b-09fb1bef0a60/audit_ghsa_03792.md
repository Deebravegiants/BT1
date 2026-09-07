# [H] Aubio is vulnerable to a NULL pointer dereference in new_aubio_notes function

## Summary
Severity: High
Advisory: GHSA-c6jq-h4jp-72pr
CVE: CVE-2018-19802
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-07-26
Source: https://github.com/advisories/GHSA-c6jq-h4jp-72pr
Type: github-advisory

## Affected
- PyPI: `aubio` — affected >=0.4.0 <0.4.9

## Details
aubio v0.4.0 to v0.4.8 has a new_aubio_onset NULL pointer dereference in `new_aubio_notes` function within `src/notes/notes.c`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19802
- https://github.com/aubio/aubio/commit/c5ee1307bdc004e43302abeca1802c2692b33a8e
- https://github.com/aubio/aubio
- https://github.com/aubio/aubio/blob/0.4.9/ChangeLog
- https://github.com/pypa/advisory-database/tree/main/vulns/aubio/PYSEC-2019-164.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IYIKPYXZIWYWWNNORSKWRCFFCP6AFMRZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OHIRMWW4JQ6UHJK4AVBJLFRLE2TPKC2W
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00012.html
