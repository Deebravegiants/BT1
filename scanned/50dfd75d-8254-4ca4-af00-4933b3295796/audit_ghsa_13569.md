# [H] Soft Serve Public Key Authentication Bypass Vulnerability when Keyboard-Interactive SSH Authentication is Enabled

## Summary
Severity: High
Advisory: GHSA-mc97-99j4-vm2v
CVE: CVE-2023-43809
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-10-02
Source: https://github.com/advisories/GHSA-mc97-99j4-vm2v
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.6.2

## Details
### Impact

A security vulnerability in Soft Serve could allow an unauthenticated, remote attacker to bypass public key authentication when keyboard-interactive SSH authentication is active, through the `allow-keyless` setting, and the public key requires additional client-side verification for example using FIDO2 or GPG. This is due to insufficient validation procedures of the public key step during SSH request handshake, granting unauthorized access if the keyboard-interaction mode is utilized. An attacker could exploit this vulnerability by presenting manipulated SSH requests using keyboard-interactive authentication mode. This could potentially result in unauthorized access to the Soft Serve.

### Patches

Users should upgrade to the latest Soft Serve version `v0.6.2` to receive the patch for this issue. 

### Workarounds

To workaround this vulnerability without upgrading, users can _temporarily_ disable Keyboard-Interactive SSH Authentication using the `allow-keyless` setting.

### References

https://github.com/charmbracelet/soft-serve/issues/389

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-mc97-99j4-vm2v
- https://nvd.nist.gov/vuln/detail/CVE-2023-43809
- https://github.com/charmbracelet/soft-serve/issues/389
- https://github.com/charmbracelet/soft-serve/commit/407c4ec72d1006cee1ff8c1775e5bcc091c2bc89
- https://github.com/charmbracelet/soft-serve
- https://github.com/charmbracelet/soft-serve/releases/tag/v0.6.2
