# [M] FlaskBB: SSRF in get_image_info() via unrestricted avatar URL

## Summary
Severity: Medium
Advisory: GHSA-xq32-9g7q-7297
CVE: CVE-2026-46556
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-xq32-9g7q-7297
Type: github-advisory

## Affected
- PyPI: `flaskbb` — affected >=0

## Details
###Summary
A Server-Side Request Forgery (SSRF) vulnerability in get_image_info() allows any authenticated user to force the server to send HTTP requests to arbitrary internal endpoints, including cloud metadata services (e.g., AWS 169.254.169.254). This is a blind SSRF with confirmed internal port scanning and internal API triggering capabilities. CVSS 6.5 Medium.

###Details
In flaskbb/utils/helpers.py (line 571), the url parameter is passed directly to requests.get(url, stream=True) without any validation of scheme, host, or IP address.
```
python# flaskbb/utils/helpers.py:571
def get_image_info(url: str):
    r = requests.get(url, timeout=(3.05, 27), stream=True)
```

Attack chain:

```
POST /user/settings/user-details (avatar URL)
→ ValidateAvatarURL.validate()    # validators.py:103
→ check_image(avatar)             # helpers.py:628
→ get_image_info(url)             # helpers.py:571
→ requests.get(url)               # No domain/IP restriction
Entry points:

/user/settings/user-details (any authenticated user)
/admin/users/<id>/edit (admin only)

```

###PoC
[submit.zip](https://github.com/user-attachments/files/26301527/submit.zip)

Log in to FlaskBB as any user
Navigate to Settings → User Details
Enter http://169.254.169.254/latest/meta-data/ as the avatar URL
Submit the form
The server sends a GET request to the internal metadata endpoint

Three exploitation channels confirmed:

Server-side request: Captured on mock metadata server
Internal port scan: check_image() returns distinct errors (CONN_REFUSED, NO_CONTENT_LENGTH, TYPE_NOT_ALLOWED, SUCCESS) that map internal network topology
Internal API triggering: Mock APIs on 127.0.0.1:9200 triggered via SSRF (deploy, shutdown, key dump endpoints)

###Impact
Any authenticated user is impacted. Attackers can force the server to request internal services, cloud metadata endpoints, or private network resources. On cloud deployments (AWS/GCP/Azure), IAM credentials can be leaked. In production, any GET-triggered internal service is reachable: CI/CD webhooks, Elasticsearch, etcd, Consul, etc.

## References
- https://github.com/flaskbb/flaskbb/security/advisories/GHSA-xq32-9g7q-7297
- https://github.com/flaskbb/flaskbb
