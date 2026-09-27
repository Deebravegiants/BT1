# [H] CVE-2023-0158

## Summary
Severity: High
Advisory: CVE-2023-0158
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2023-0158
Type: osv

## Details
NLnet Labs Krill supports direct access to the RRDP repository content through its built-in web server at the "/rrdp" endpoint. Prior to 0.12.1 a direct query for any existing directory under "/rrdp/", rather than an RRDP file such as "/rrdp/notification.xml" as would be expected, causes Krill to crash. If the built-in "/rrdp" endpoint is exposed directly to the internet, then malicious remote parties can cause the publication server to crash. The repository content is not affected by this, but the availability of the server and repository can cause issues if this attack is persistent and is not mitigated.

## References
- https://www.nlnetlabs.nl/downloads/krill/CVE-2023-0158.txt
