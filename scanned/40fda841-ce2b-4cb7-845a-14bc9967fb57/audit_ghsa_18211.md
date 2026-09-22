# [H] Rancher CLI SAML authentication is vulnerable to phishing attacks

## Summary
Severity: High
Advisory: GHSA-v3vj-5868-2ch2
CVE: CVE-2024-58267
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-v3vj-5868-2ch2
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.12.0 <2.12.2
- Go: `github.com/rancher/rancher` — affected >=2.11.0 <2.11.6
- Go: `github.com/rancher/rancher` — affected >=2.10.0 <2.10.10
- Go: `github.com/rancher/rancher` — affected >=2.9.0 <2.9.12

## Details
### Impact

A vulnerability has been identified within Rancher Manager whereby the SAML authentication from the Rancher CLI  tool is vulnerable to phishing attacks. The custom authentication protocol for SAML-based providers can be abused to steal Rancher’s authentication tokens.

Rancher Manager deployments without SAML authentication enabled are not affected by this vulnerability.

An attacker can generate a phishing SAML login URL which contains a `publicKey` and `requestId` controlled by the attacker. The attacker can then give the link to another user (eg: admin) and if the victim goes to the link unsuspectingly, they might not notice the bad parameters in the URL. The user will be prompted to login and might believe that its session has ended so they need to re-login. By clicking on the link, they will be logged in and an encrypted token will be created with the attacker's public key. The attacker can then decrypt the victim’s Rancher token, enabling the attack

Please consult the associated [MITRE ATTACK Techniques - Privilege Escalation](https://attack.mitre.org/tactics/TA0004/) for further information about this category of attack.

### Patches

This vulnerability is addressed by changes in both Rancher Manager and the CLI. The fixed versions:

1. The Rancher CLI now reports the `requestId` that is relevant to the authentication session in process as a separate message to the terminal, making it easier for the user to identify and compare.
2. The Rancher login page for SAML authentication will display a suitable warning to ensure that the user seeing the login page is aware of the login process with the related `requestId`, enabling users to verify whether the request was intended or not.

Patched versions of Rancher include releases v2.12.2, v2.11.6, v2.10.10, and v2.9.12.

### Workarounds

If you cannot update to one of the fixed versions, make sure to check the URL printed by the Rancher CLI when performing a SAML authentication flow, especially the `requestId` parameter. The URL and the `requestId` printed by the CLI must be the same URL that you access and see when finalizing the SAML authentication flow in your browser for the Rancher UI. The URL has the format:

-  `<rancher_ui_address>/dashboard/auth/login?requestId=<requestid>&publicKey=<pubkey>&responseType=<responsetype>` 

If the URL presented in the browser is different from the one logged by the CLI, the user must not proceed with the login, as they might be under a phishing attack.

### References

If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-v3vj-5868-2ch2
- https://nvd.nist.gov/vuln/detail/CVE-2024-58267
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2024-58267
- https://github.com/rancher/rancher
- https://pkg.go.dev/vuln/GO-2025-3984
