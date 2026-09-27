# [M] Mealie contains a DoS vulnerability in recipe importer

## Summary
Severity: Medium
Advisory: CVE-2024-31992
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2024-31992
Type: osv

## Details
Mealie is a self hosted recipe manager and meal planner. Prior to 1.4.0, the safe_scrape_html function utilizes a user-controlled URL to issue a request to a remote server, however these requests are not rate-limited. While there are efforts to prevent DDoS by implementing a timeout on requests, it is possible for an attacker to issue a large number of requests to the server which will be handled in batches based on the configuration of the Mealie server. The chunking of responses is helpful for mitigating memory exhaustion on the Mealie server, however a single request to an arbitrarily large external file (e.g. a Debian ISO) is often sufficient to completely saturate a CPU core assigned to the Mealie container. Without rate limiting in place, it is possible to not only sustain traffic against an external target indefinitely, but also to exhaust the CPU resources assigned to the Mealie container. This vulnerability is fixed in 1.4.0.

## References
- https://github.com/mealie-recipes/mealie/blob/mealie-next/mealie/services/scraper/scraper_strategies.py#L27-L70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31992.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31992
- https://securitylab.github.com/advisories/GHSL-2023-225_GHSL-2023-226_Mealie/
- https://github.com/mealie-recipes/mealie/commit/2a3463b7466bc297aede50046da9550d919ec56f
- https://github.com/mealie-recipes/mealie/pull/3368
