# [M] Information Disclosure Vulnerability in Privacy Center of SERVER_SIDE_FIDES_API_URL

## Summary
Severity: Medium
Advisory: GHSA-53q7-4874-24qg
CVE: CVE-2024-31223
CWE: CWE-497
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-53q7-4874-24qg
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=2.19.0 <2.39.2

## Details
`SERVER_SIDE_FIDES_API_URL` is a server-side configuration environment variable used by the Fides Privacy Center to communicate with the Fides webserver backend. The value of this variable is a URL which typically includes a private IP address, private domain name, and/or port.

This vulnerability allows an unauthenticated attacker to make a HTTP GET request from the Privacy Center that discloses the value of this server-side URL.

### Impact

Disclosure of server-side configuration giving an attacker information on server-side ports, private IP addresses, and/or private domain names.

### Patches
The vulnerability has been patched in Fides version `2.39.2`. Users are advised to upgrade to this version or later to secure their systems against this threat.

### Workarounds
There are no workarounds.

### Proof of Concept

1. Set the value of the environment variable `FIDES_PRIVACY_CENTER__SERVER_SIDE_FIDES_API_URL` of your Fides Privacy Center container before start-up to a private value such as `https://some.private.domain.name/api/v1` and start the Privacy Center application.

2. Once the application is up, perform a HTTP GET request of the Privacy Center's main page e.g. `https://privacy.example.com` . The value of `SERVER_SIDE_FIDES_API_URL` is returned in the response's body.


```
~ ❯ curl -s https://privacy.example.com/ | \
grep '__NEXT_DATA__' | \
sed 's/.*<script id="__NEXT_DATA__" type="application\/json">//;s/<\/script>.*//' | \
jq '.props.serverEnvironment.settings.SERVER_SIDE_FIDES_API_URL'
"https://some.private.domain.name/api/v1"
```

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-53q7-4874-24qg
- https://nvd.nist.gov/vuln/detail/CVE-2024-31223
- https://github.com/ethyca/fides/commit/0555080541f18a5aacff452c590ac9a1b56d7097
- https://github.com/ethyca/fides/commit/cd510216b281de5443ec1c126add95cc5be0970a
- https://github.com/ethyca/fides
