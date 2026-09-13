# [M] Datavane TIS v5.0.0 XXE Injection via doEditWorkflow Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-69101
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-69101
Type: osv

## Details
Datavane TIS v5.0.0 contains an XML external entity (XXE) injection vulnerability that allows authenticated attackers to perform server-side request forgery and out-of-band file exfiltration by supplying a crafted taskScript payload to the doEditWorkflow endpoint, which processes XML through an unhardened DocumentBuilderFactory with external entities and DTD loading enabled. Attackers can send a malicious XML document containing an external DTD reference to the edit_workflow action, causing the server to issue outbound HTTP requests to attacker-controlled infrastructure and exfiltrate local files readable by the TIS process user, including configuration files and Derby database credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69101.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69101
- https://www.vulncheck.com/advisories/datavane-tis-xxe-injection-via-doeditworkflow-endpoint
- https://github.com/datavane/tis/issues/496
- https://github.com/datavane/tis/commit/2a84a1b84218a303e3e0a4823023363d5a7abfa1
- https://github.com/datavane/tis
