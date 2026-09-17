# [M] Gradio vulnerable to arbitrary file read and proxying of arbitrary URLs

## Summary
Severity: Medium
Advisory: GHSA-3qqg-pgqq-3695
CVE: CVE-2023-34239
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-3qqg-pgqq-3695
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <3.34.0

## Details
### Impact
There are two separate security vulnerabilities here: (1) a security vulnerability that allows users to read arbitrary files on the machines that are running shared Gradio apps (2) the ability of users to use machines that are sharing Gradio apps to proxy arbitrary URLs

### Patches
Both problems have been solved, please upgrade `gradio` to `3.34.0` or higher

### Workarounds
Not possible to workaround except by taking down any shared Gradio apps

### References
Relevant PRs:
* https://github.com/gradio-app/gradio/pull/4406
* https://github.com/gradio-app/gradio/pull/4370

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-3qqg-pgqq-3695
- https://nvd.nist.gov/vuln/detail/CVE-2023-34239
- https://github.com/gradio-app/gradio/pull/4370
- https://github.com/gradio-app/gradio/pull/4406
- https://github.com/gradio-app/gradio/commit/37967617bd97615fb6f3b44e7750c0e0be58479a
- https://github.com/gradio-app/gradio/commit/37967617bd97615fb6f3b44e7750c0e0be58479a#diff-324a7165f5d5a8823a28b76f5653fa45f32c8144c82b2e528882c97c7eae534f
- https://github.com/gradio-app/gradio/commit/cd64130d54e678525774bbb200ef9c7166fa1543
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2023-90.yaml
