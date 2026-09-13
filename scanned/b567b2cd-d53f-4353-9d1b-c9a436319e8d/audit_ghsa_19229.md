# [C] OPKSSH Vulnerable to Authentication Bypass 

## Summary
Severity: Critical
Advisory: GHSA-56wx-66px-9j66
CVE: CVE-2025-4658
CWE: CWE-305
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-05-13
Source: https://github.com/advisories/GHSA-56wx-66px-9j66
Type: github-advisory

## Affected
- Go: `github.com/openpubkey/opkssh` — affected >=0 <0.5.0

## Details
### Impact

Versions of OpenPubkey library prior to 0.10.0 contained a vulnerability that would allow a specially crafted JWS to bypass signature verification. As OPKSSH depends on the OpenPubkey library for authentication, this vulnerability in OpenPubkey also applies to OPKSSH versions prior to 0.5.0 and would allow an attacker to bypass OPKSSH authentication.

### Patches

The vulnerability does not exist in more recent versions of OPKSSH. his only impacts OPKSSH  when used to verify ssh keys on a server, the OPKSSH client is unaffected. To remediate upgrade to a version of OPKSSH v0.5.0 or greater.

To determine if you are vulnerable run on your server:

```bash
opkssh --version
```

If the version is less than 0.5.0 you should upgrade. To upgrade to the latest version run:

```bash
wget -qO- "https://raw.githubusercontent.com/openpubkey/opkssh/main/scripts/install-linux.sh" | sudo bash
``` 


### References

[CVE-2025-4658](https://www.cve.org/CVERecord?id=CVE-2025-4658)

The upstream vulnerability in OpenPubkey is [CVE-2025-3757](https://www.cve.org/CVERecord?id=CVE-2025-3757) and has the security advisory https://github.com/openpubkey/openpubkey/security/advisories/GHSA-537f-gxgm-3jjq

## References
- https://github.com/openpubkey/opkssh/security/advisories/GHSA-56wx-66px-9j66
- https://nvd.nist.gov/vuln/detail/CVE-2025-4658
- https://github.com/openpubkey/opkssh
