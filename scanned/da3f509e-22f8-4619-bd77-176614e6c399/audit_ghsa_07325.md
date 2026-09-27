# [H] Rancher Fleet has Unauthenticated Webhook: Regex Injection via Unsanitized Repository URL Components

## Summary
Severity: High
Advisory: GHSA-jmf4-m7j9-g72r
CVE: CVE-2026-44937
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-jmf4-m7j9-g72r
Type: github-advisory

## Affected
- Go: `github.com/rancher/fleet` — affected >=0.15.0 <0.15.2
- Go: `github.com/rancher/fleet` — affected >=0.14.0 <0.14.6
- Go: `github.com/rancher/fleet` — affected >=0.13.0 <0.13.11
- Go: `github.com/rancher/fleet` — affected >=0.12.0 <0.12.15

## Details
### Impact
A vulnerability has been identified in Fleet when the webhook endpoint is configured without a secret; an attacker can forge webhook requests. The attacker doesn't need to know the specific repository or path configured in the GitRepo resource to make Fleet process these requests.

An attacker can exploit this vulnerability to cause the following impacts:
1. Trigger continuous repository re-cloning, which increases network traffic and can deplete resources on the management cluster.
2. Downgrade running services to any historical revision available in the remote Git repository. This risk applies if the attacker has read access to the target Git repository and knows its configured path.

Please consult the associated  [MITRE ATT&CK - Technique - T1499.004: Endpoint Denial of Service](https://attack.mitre.org/techniques/T1499/) for further information about this category of attack.

### Patches
To resolve this vulnerability, upgrade Fleet to a patched version. This upgrade version escapes the URL and path to the remote repository received from webhooks, which prevents regular expressions from being used as a replacement for the URL and path.

Patched versions of Fleet include releases `v0.15.2`, `v0.14.6`, `0.13.11`, and `v0.12.15`.

### Workarounds
If you can't upgrade to a fixed version, please make sure to only enable webhooks with a shared secret.

### Credits

This security issue was reported by the following collaborators according to our responsible disclosure policy:

- Radisauskas Arnoldas from NATO and the NATO Cyber Security Centre (NCSC).

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/fleet/security/advisories/GHSA-jmf4-m7j9-g72r
- https://github.com/rancher/fleet
