# [M] Mealie vulnerable to a GET-based SSRF in recipe importer (GHSL-2023-225)

## Summary
Severity: Medium
Advisory: CVE-2024-31991
CVSS: 4.1 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2024-31991
Type: osv

## Details
Mealie is a self hosted recipe manager and meal planner. Prior to 1.4.0, the safe_scrape_html function utilizes a user-controlled URL to issue a request to a remote server. Based on the content of the response, it will either parse the content or disregard it. This function, nor those that call it, add any restrictions on the URL that can be provided, nor is it restricted to being an FQDN (i.e., an IP address can be provided). As this function’s return will be handled differently by its caller depending on the response, it is possible for an attacker to use this functionality to positively identify HTTP(s) servers on the local network with any IP/port combination. This issue can result in any authenticated user being able to map HTTP servers on a local network that the Mealie service has access to. Note that by default any user can create an account on a Mealie server, and that the default changeme@example.com user is available with its hard-coded password. This vulnerability is fixed in 1.4.0.

## References
- https://github.com/mealie-recipes/mealie/blob/mealie-next/mealie/services/scraper/scraper_strategies.py#L27-L70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31991.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31991
- https://securitylab.github.com/advisories/GHSL-2023-225_GHSL-2023-226_Mealie/
- https://github.com/mealie-recipes/mealie/commit/2a3463b7466bc297aede50046da9550d919ec56f
- https://github.com/mealie-recipes/mealie/pull/3368
