# [M] Injection of arbitrary HTML/JavaScript code through the media download URL

## Summary
Severity: Medium
Advisory: GHSA-6784-9c82-vr85
CVE: CVE-2024-47617
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-6784-9c82-vr85
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=2.6.0 <2.6.5
- Packagist: `sulu/sulu` — affected >=2.0.0 <2.5.21

## Details
### Impact

This vulnerability allows an attacker to inject arbitrary HTML/JavaScript code through the media download URL in Sulu CMS. It affects the SuluMediaBundle component. The vulnerability is a Reflected Cross-Site Scripting (XSS) issue, which could potentially allow attackers to steal sensitive information, manipulate the website's content, or perform actions on behalf of the victim.

### Patches

The problem has not been patched yet. Users should upgrade to patched versions once they become available. Currently affected versions are:

* 2.6.4
* 2.5.20

### Workarounds

Until an official patch is released, users can implement additional input validation and output encoding for the 'slug' parameter in the MediaStreamController's downloadAction method. Alternatively, configuring a Web Application Firewall (WAF) to filter potentially malicious input could serve as a temporary mitigation.

### References

* GitHub repository: https://github.com/sulu/sulu
* Vulnerable code: https://github.com/sulu/sulu/blob/2.6/src/Sulu/Bundle/MediaBundle/Controller/MediaStreamController.php#L106

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-6784-9c82-vr85
- https://nvd.nist.gov/vuln/detail/CVE-2024-47617
- https://github.com/sulu/sulu/commit/a5a5ae555d282e88ff8559d38cfb46dea7939bda
- https://github.com/sulu/sulu/commit/eeacd14b6cf55f710084788140d40ebb00314b29
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/blob/2.6/src/Sulu/Bundle/MediaBundle/Controller/MediaStreamController.php#L106
