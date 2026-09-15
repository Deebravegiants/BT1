# [M] OpenStack magnum vulnerable to time-of-check to time-of-use (TOCTOU) attack

## Summary
Severity: Medium
Advisory: GHSA-jx7x-9r98-h5xr
CVE: CVE-2024-28718
CWE: CWE-367
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-jx7x-9r98-h5xr
Type: github-advisory

## Affected
- PyPI: `magnum` — affected >=0 <14.1.2
- PyPI: `magnum` — affected >=17.0.0.0rc1 <17.0.2
- PyPI: `magnum` — affected >=16.0.0.0rc1 <16.0.2
- PyPI: `magnum` — affected >=15.0.0.0rc1 <15.0.2

## Details
An issue in OpenStack magnum yoga-eom version allows a remote attacker to execute arbitrary code via the cert_manager.py. component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28718
- https://github.com/openstack/magnum/commit/272fd686d8c8bf5954e9e7d3bc991ff27e46184d
- https://github.com/openstack/magnum/commit/312aa6a86ac8e62f6ed4f1e9473fdabbbb7a4b1e
- https://github.com/openstack/magnum/commit/883b40b5b0ecfc5f78758143c0d3c754458f12b7
- https://github.com/openstack/magnum/commit/e79907c521149872c1b495355a3a7b3a0c7e3479
- https://bugs.launchpad.net/magnum/+bug/2047690
- https://gist.github.com/Fewword/f098d8d6375ac25e27b18c0e57be532f
- https://github.com/openstack/magnum
- https://review.opendev.org/c/openstack/magnum/+/907305
