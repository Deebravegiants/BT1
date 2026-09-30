# [C] pyLoad: Server-Side Request Forgery via Download Link Submission Enables Cloud Metadata Exfiltration

## Summary
Severity: Critical
Advisory: GHSA-m74m-f7cr-432x
CVE: CVE-2026-33992
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-m74m-f7cr-432x
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
## Summary

PyLoad's download engine accepts arbitrary URLs without validation, enabling Server-Side Request Forgery (SSRF) attacks. An authenticated attacker can exploit this to access internal network services and exfiltrate cloud provider metadata. On DigitalOcean droplets, this exposes sensitive infrastructure data including droplet ID, network configuration, region, authentication keys, and SSH keys configured in user-data/cloud-init.

## Details

The vulnerability exists in PyLoad's download package functionality (`/api/addPackage` endpoint), which directly passes user-supplied URLs to the download engine without validating the destination. The affected code in `src/pyload/webui/app/blueprints/api_blueprint.py`:

```python
@bp.route("/addPackage", methods=["POST"], endpoint="add_package")
@login_required
def add_package():
    name = flask.request.form["add_name"]
    links = flask.request.form["add_links"].split("\n")
    # ... validation omitted ...
    api.add_package(name, links, dest)  # No URL validation
```

The download engine in `src/pyload/core/managers/download.py` accepts any URL scheme and initiates HTTP requests to arbitrary destinations, including internal network addresses and cloud metadata endpoints.

## Proof of Concept

**Live Demo Instance:** http://143.244.141.81:8000  
**Credentials:** `pyload` / `pyload`

- Login into the pyload application
- Navigate to package tab and enter the package name and fill the Link section with the following URL

```
http://169.254.169.254/metadata/v1.json
```

<img width="1851" height="786" alt="image" src="https://github.com/user-attachments/assets/18e7aedf-7663-4a57-8f3e-5200be2c958e" />

- Now navigate to Files section and download the link.

<img width="1429" height="870" alt="image" src="https://github.com/user-attachments/assets/9b8b9cd6-afb7-461c-b058-a3cc4f26e2e6" />

- It was observed that we are able to Read the Digital Ocean Metadata

<img width="1872" height="837" alt="image" src="https://github.com/user-attachments/assets/d30d2d74-53e9-46f8-8206-894a275ac831" />

The downloaded `v1.json` file contains sensitive cloud infrastructure data:
- **Droplet ID**: Unique identifier for the instance
- **Network Configuration**: Public/private IP addresses, VPC topology
- **Authentication Keys**: Cloud provider auth tokens
- **SSH Keys**: Public keys configured in droplet metadata
- **Region and Datacenter**: Infrastructure location

## Impact

**Vulnerability Type:** Server-Side Request Forgery (SSRF)  
**CVSS Score:** 7.7 - 9.1 (High to Critical, depending on cloud deployment)

### Affected Systems
- All PyLoad installations (version 0.5.0 and potentially earlier)
- **Critical Impact** on cloud deployments (AWS EC2, DigitalOcean, Google Cloud, Azure) where metadata contains:
  - IAM credentials (AWS)
  - SSH private keys (configured in user-data)
  - API tokens and secrets
  - Database credentials stored in cloud-init

### Attack Requirements
- Valid PyLoad user account (any role - ADMIN or USER)
- Network connectivity to PyLoad instance

### Security Impact
1. **Cloud Metadata Theft**: Complete exfiltration of instance metadata
2. **Lateral Movement**: Discovery and enumeration of internal network services
3. **Credential Exposure**: Theft of cloud IAM credentials, SSH keys, API tokens
4. **Infrastructure Mapping**: Network topology, IP addressing, service discovery

## Remediation

Implement URL validation in the download engine:
1. Whitelist allowed URL schemes (http/https only)
2. Block requests to private IP ranges (RFC 1918, link-local addresses)
3. Block cloud metadata endpoints (169.254.169.254, metadata.google.internal, etc.)
4. Implement request destination validation before initiating downloads

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-m74m-f7cr-432x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33992
- https://github.com/pyload/pyload/commit/b76b6d4ee5e32d2118d26afdee1d0a9e57d4bfe8
- https://github.com/pyload/pyload
