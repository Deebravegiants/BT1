# [H] Pillow subject to DoS via SAMPLESPERPIXEL tag

## Summary
Severity: High
Advisory: GHSA-q4mp-jvh2-76fj
CVE: CVE-2022-45199
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-14
Source: https://github.com/advisories/GHSA-q4mp-jvh2-76fj
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=9.2.0 <9.3.0

## Details
Pillow starting with 9.2.0 and prior to 9.3.0 allows denial of service via SAMPLESPERPIXEL. A large value in the SAMPLESPERPIXEL tag could lead to a memory and runtime DOS in TiffImagePlugin.py when setting up the context for image decoding. This issue has been patched in version 9.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45199
- https://github.com/python-pillow/Pillow/pull/6700
- https://github.com/python-pillow/Pillow/commit/2444cddab2f83f28687c7c20871574acbb6dbcf3
- https://bugs.gentoo.org/878769
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2022-42980.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/9.3.0
- https://security.gentoo.org/glsa/202211-10
