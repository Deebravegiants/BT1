# [C] Code Injection in PyTorch Lightning

## Summary
Severity: Critical
Advisory: GHSA-r5qj-cvf9-p85h
CVE: CVE-2022-0845
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-06
Source: https://github.com/advisories/GHSA-r5qj-cvf9-p85h
Type: github-advisory

## Affected
- PyPI: `pytorch-lightning` — affected >=0 <1.6.0

## Details
PyTorch Lightning version 1.5.10 and prior is vulnerable to code injection. An attacker could execute commands on the target OS running the operating system by setting the `PL_TRAINER_GPUS` when using the `Trainer` module. A [patch](https://github.com/pytorchlightning/pytorch-lightning/commit/8b7a12c52e52a06408e9231647839ddb4665e8ae) is included in the `1.6.0` release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0845
- https://github.com/PyTorchLightning/pytorch-lightning/pull/12212
- https://github.com/pytorchlightning/pytorch-lightning/commit/8b7a12c52e52a06408e9231647839ddb4665e8ae
- https://github.com/advisories/GHSA-r5qj-cvf9-p85h
- https://github.com/pypa/advisory-database/tree/main/vulns/pytorch-lightning/PYSEC-2022-181.yaml
- https://github.com/pytorchlightning/pytorch-lightning
- https://huntr.dev/bounties/a795bf93-c91e-4c79-aae8-f7d8bda92e2a
