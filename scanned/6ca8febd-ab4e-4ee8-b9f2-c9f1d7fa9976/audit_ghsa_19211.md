# [C] Crayfish Allows Remote Code Execution via hypercube X-Islandora-Args Header

## Summary
Severity: Critical
Advisory: GHSA-c2p2-hgjg-9r3f
CWE: CWE-150, CWE-74
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-02-12
Source: https://github.com/advisories/GHSA-c2p2-hgjg-9r3f
Type: github-advisory

## Affected
- Packagist: `islandora/crayfish` — affected >=0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Remote code execution is possible in web-accessible installations of hypercube. 

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Not yet, though no patch is neccessary if your installation of the microservices is behind a firewall.  See below.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

The exploit requires making a request against Hypercube's endpoints; therefore, the ability to make use of the exploit is much reduced if the microservice is not directly accessible from the Internet, so: Prevent general access from the Internet from hitting Hypercube.  Furthermore, if you've used any of the official installation methods, your Crayfish will be behind a firewall and there is no work neccessary.

The webserver might be made to validate the structure of headers passed, but that would only be neccessary if you publicly exposed the endpoint. Standard security practices should be applied.

### References
_Are there any links users can visit to find out more?_

- XBOW-024-074

## References
- https://github.com/Islandora/Crayfish/security/advisories/GHSA-c2p2-hgjg-9r3f
- https://github.com/Islandora/Crayfish
