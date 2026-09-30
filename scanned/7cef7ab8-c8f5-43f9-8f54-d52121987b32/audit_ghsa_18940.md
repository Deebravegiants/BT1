# [C] Ray's New Token Authentication is Disabled By Default

## Summary
Severity: Critical
Advisory: GHSA-gx77-xgc2-4888
CVE: CVE-2025-34351
CWE: CWE-1188, CWE-304
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-27
Source: https://github.com/advisories/GHSA-gx77-xgc2-4888
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=0

## Details
Anyscale Ray 2.52.0 contains an insecure default configuration in which token-based authentication for Ray management interfaces (including the dashboard and Jobs API) is disabled unless explicitly enabled by setting RAY_AUTH_MODE=token. In the default unauthenticated state, a remote attacker with network access to these interfaces can submit jobs and execute arbitrary code on the Ray cluster. NOTE: The vendor plans to enable token authentication by default in a future release. They recommend enabling token authentication to protect your cluster from unauthorized access.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-w8vc-465m-jjw6
- https://nvd.nist.gov/vuln/detail/CVE-2025-34351
- https://docs.ray.io/en/latest/ray-security/token-auth.html
- https://github.com/ray-project/ray
- https://github.com/ray-project/ray/releases/tag/ray-2.52.0
- https://www.cve.org/resourcessupport/allresources/cnarules#section_4-1_Vulnerability_Determination
- https://www.linkedin.com/posts/jonathan-leitschuh_the-latest-piece-of-mind-bending-research-activity-7396976425997606912-qizE
- https://www.oligo.security/blog/shadowray-2-0-attackers-turn-ai-against-itself-in-global-campaign-that-hijacks-ai-into-self-propagating-botnet
- https://www.oligo.security/blog/shadowray-attack-ai-workloads-actively-exploited-in-the-wild
- https://www.vulncheck.com/advisories/anyscale-ray-token-authentication-disabled-by-default-insecure-configuration
