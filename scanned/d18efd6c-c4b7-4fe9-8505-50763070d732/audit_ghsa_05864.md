# [M] Ghost: Server-side request forgery via DNS rebinding in external request handling

## Summary
Severity: Medium
Advisory: GHSA-ch52-px8q-f22j
CVE: CVE-2026-53945
CWE: CWE-367, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-ch52-px8q-f22j
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.0.9 <6.21.2

## Details
### Impact

Ghost’s private-IP check for outbound HTTP requests could be bypassed via DNS rebinding, allowing an attacker to coerce the Ghost server into reaching hosts on internal networks through features that issue external fetches.

### Vulnerable versions

This vulnerability is present in Ghost from v6.0.9 up to v6.21.0.

### Patches

v6.21.1 contains a fix for this issue. 

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### Workarounds

If upgrading immediately is not possible, operators can reduce exposure by preventing the Ghost server from reaching sensitive internal ranges at the network layer — for example, egress firewall rules that block the Ghost process from initiating connections to RFC1918 networks, loopback, link-local (including `169.254.169.254`) and any other internal service ranges. Disabling features that trigger outbound fetches (oEmbed, webmentions, recommendations) will further limit the attack surface but does not remove the underlying issue.

### References

Ghost thanks Oluwaseun Esther Folorunsho, Lakshmikanthan K ([@l3tchupkt](https://github.com/l3tchupkt)), [Offgrid Security](https://www.offgridsec.com/), and Baki for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-ch52-px8q-f22j
- https://nvd.nist.gov/vuln/detail/CVE-2026-53945
- https://github.com/TryGhost/Ghost/pull/26754
- https://github.com/TryGhost/Ghost/commit/07d604100eb3df5c9b382fce6232928c96329448
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.21.1
