# [M] homepage DNS rebinding vulnerability (GHSL-2024-096)

## Summary
Severity: Medium
Advisory: CVE-2024-42364
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-08-23
Source: https://osv.dev/vulnerability/CVE-2024-42364
Type: osv

## Details
Homepage is a highly customizable homepage with Docker and service API integrations. The default setup of homepage 0.9.1 is vulnerable to DNS rebinding. Homepage is setup without certificate and authentication by default, leaving it to vulnerable to DNS rebinding. In this attack, an attacker will ask a user to visit his/her website. The attacker website will then change the DNS records of their domain from their IP address to the internal IP address of the homepage instance. To tell which IP addresses are valid, we can rebind a subdomain to each IP address we want to check, and see if there is a response. Once potential candidates have been found, the attacker can launch the attack by reading the response of the webserver after the IP address has changed. When the attacker domain is fetched, the response will be from the homepage instance, not the attacker website, because the IP address has been changed. Due to a lack of authentication, a user’s private information such as API keys (fixed after first report) and other private information can then be extracted by the attacker website.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42364.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42364
- https://securitylab.github.com/advisories/GHSL-2024-096_homepage/
