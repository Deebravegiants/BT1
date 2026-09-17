# [C] Remote Code Execution (RCE) vulnerability in jupyterlab extension template  `update-integration-tests` GitHub Action

## Summary
Severity: Critical
Advisory: BIT-jupyterlab-2024-39700
Aliases: CVE-2024-39700, GHSA-45gq-v5wm-82wg, PYSEC-2024-322
Ecosystem: Bitnami
Published: 2025-09-09
Source: https://osv.dev/vulnerability/BIT-jupyterlab-2024-39700
Type: osv

## Affected
- Bitnami: `jupyterlab` — affected >=0 <4.3.0

## Details
JupyterLab extension template is a  `copier` template for JupyterLab extensions. Repositories created using this template with `test` option include `update-integration-tests.yml` workflow which has an RCE vulnerability. Extension authors hosting their code on GitHub are urged to upgrade the template to the latest version. Users who made changes to `update-integration-tests.yml`, accept overwriting of this file and re-apply your changes later. Users may wish to temporarily disable GitHub Actions while working on the upgrade. We recommend rebasing all open pull requests from untrusted users as actions may run using the version from the `main` branch at the time when the pull request was created. Users who are upgrading from template version prior to 4.3.0 may wish to leave out proposed changes to the release workflow for now as it requires additional configuration.

## References
- https://github.com/jupyterlab/extension-template/commit/035e78c1c65bcedee97c95bb683abe59c96bc4e6
- https://github.com/jupyterlab/extension-template/security/advisories/GHSA-45gq-v5wm-82wg
- https://nvd.nist.gov/vuln/detail/CVE-2024-39700
