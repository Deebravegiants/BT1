# [M] Salt preflight script could be attacker controlled

## Summary
Severity: Medium
Advisory: GHSA-4277-m35q-7c9w
CVE: CVE-2023-34049
CWE: CWE-340
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-14
Source: https://github.com/advisories/GHSA-4277-m35q-7c9w
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3005.4
- PyPI: `salt` — affected >=3006.0rc1 <3006.4

## Details
The Salt-SSH pre-flight option copies the script to the target at a predictable path, which allows an attacker to force Salt-SSH to run their script. If an attacker has access to the target VM and knows the path to the pre-flight script before it runs they can ensure Salt-SSH runs their script with the privileges of the user running Salt-SSH. Do not make the copy path on the target predictable and ensure we check return codes of the scp command if the copy fails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34049
- https://github.com/saltstack/salt/commit/286d55eb5a6e6bf9428405bdf5632b419bdf8444
- https://github.com/saltstack/salt/commit/7a14112f2a16ce70e3c3e1862c92e37af5f2c7a4
- https://github.com/saltstack/salt
- https://saltproject.io/security-announcements/2023-10-27-advisory
