# [C] Trivy ecosystem supply chain briefly compromised

## Summary
Severity: Critical
Advisory: CVE-2026-33634
Aliases: GHSA-69fq-xp46-6x23, GO-2026-4919
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-33634
Type: osv

## Details
Trivy is a security scanner. On March 19, 2026, a threat actor used compromised credentials to publish a malicious Trivy v0.69.4 release, force-push 76 of 77 version tags in `aquasecurity/trivy-action` to credential-stealing malware, and replace all 7 tags in `aquasecurity/setup-trivy` with malicious commits. This incident is a continuation of the supply chain attack that began in late February 2026. Following the initial disclosure on March 1, credential rotation was performed but was not atomic (not all credentials were revoked simultaneously). The attacker could have use a valid token to exfiltrate newly rotated secrets during the rotation window (which lasted a few days). This could have allowed the attacker to retain access and execute the March 19 attack. Affected components include the `aquasecurity/trivy` Go / Container image version 0.69.4, the `aquasecurity/trivy-action` GitHub Action versions 0.0.1 – 0.34.2 (76/77), and the`aquasecurity/setup-trivy` GitHub Action versions 0.2.0 – 0.2.6, prior to the recreation of 0.2.6 with a safe commit. Known safe versions include versions 0.69.2 and 0.69.3 of the Trivy binary, version 0.35.0 of trivy-action, and version 0.2.6 of setup-trivy. Additionally, take other mitigations to ensure the safety of secrets. If there is any possibility that a compromised version ran in one's environment, all secrets accessible to affected pipelines must be treated as exposed and rotated immediately. Check whether one's organization pulled or executed Trivy v0.69.4 from any source. Remove any affected artifacts immediately. Review all workflows using `aquasecurity/trivy-action` or `aquasecurity/setup-trivy`. Those who referenced a version tag rather than a full commit SHA should check workflow run logs from March 19–20, 2026 for signs of compromise. Look for repositories named `tpcp-docs` in one's GitHub organization. The presence of such a repository may indicate that the fallback exfiltration mechanism was triggered and secrets were successfully stolen. Pin GitHub Actions to full, immutable commit SHA hashes, don't use mutable version tags.

## References
- https://github.com/aquasecurity/trivy/discussions/10425
- https://inspector.pypi.io/project/litellm/1.82.7/packages/79/5f/b6998d42c6ccd32d36e12661f2734602e72a576d52a51f4245aef0b20b4d/litellm-1.82.7-py3-none-any.whl/litellm/proxy/proxy_server.py#line.130
- https://inspector.pypi.io/project/litellm/1.82.8/packages/f6/2c/731b614e6cee0bca1e010a36fd381fba69ee836fe3cb6753ba23ef2b9601/litellm-1.82.8.tar.gz/litellm-1.82.8/litellm_init.pth#line.1
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-33634
- https://github.com/BerriAI/litellm/issues/24518#issuecomment-4127436387
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33634.json
- https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23
- https://github.com/pypa/advisory-database/tree/main/vulns/litellm/PYSEC-2026-2.yaml
- https://github.com/team-telnyx/telnyx-python/security/advisories/GHSA-955r-262c-33jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33634
- https://www.microsoft.com/en-us/security/blog/2026/03/24/detecting-investigating-defending-against-trivy-supply-chain-compromise/
- https://github.com/BerriAI/litellm/issues/24518
- https://docs.litellm.ai/blog/security-update-march-2026
- https://futuresearch.ai/blog/litellm-pypi-supply-chain-attack
- https://www.wiz.io/blog/teampcp-attack-kics-github-action
- https://rosesecurity.dev/2026/03/20/typosquatting-trivy.html
