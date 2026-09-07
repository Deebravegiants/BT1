# [M] RustFS Logs Sensitive Credentials in Plaintext

## Summary
Severity: Medium
Advisory: GHSA-r54g-49rx-98cr
CVE: CVE-2026-24762
CWE: CWE-532
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-r54g-49rx-98cr
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=1.0.0-alpha.13 <1.0.0-alpha.82

## Details
### Summary
RustFS logs sensitive credential material (access key, secret key, session token) to application logs at INFO level. This results in credentials being recorded in plaintext in log output, which may be accessible to internal or external log consumers and could lead to compromise of sensitive credentials. This vulnerability is classified as an information disclosure issue (CWE-532).

### Details
The server writes newly generated STS credential information including the access key, secret key, and session token to logs. The following excerpts from application logs demonstrate this:

```
[2026-01-17 09:13:23.127767 +11:00] INFO [rustfs::admin::handlers::sts] [rustfs/src/admin/handlers/sts.rs:138] [rustfs-worker:ThreadId(4)] AssumeRole get new_cred Credentials { access_key: "5UGH6TM44IPA81AH1WZE", secret_key: "3BQ-KnO_iB5ovmd5SU4wIK6sFfaPTliftvQ_iNLS", session_token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJleHAiOjE3Njg2NDQ4MDMsInBhcmVudCI6InJ1c3Rmc2FkbWluIn0.F9ZhARXyU0cB6QoFMElKK5tns_RFQM9WlpMiGVuuDOpOfNrbEKE_9IK1oaJ_yqDsBlK115uYOcQcGohjgUPhOQ", expiration: Some(2026-01-17 10:13:23.0 +00:00:00), status: "on", parent_user: "rustfsadmin", groups: None, claims: None, name: None, description: None }
```
By inspecting logs, an attacker or unauthorized internal user with access to logs could retrieve these credentials and use them to authenticate to RustFS services or perform other unauthorized actions.

### Impact
- Information Exposure: Plaintext authentication credentials appear in log files that may be retained, backed up, or forwarded to centralized logging systems.
- Credential Compromise: Access keys, secret keys, and session tokens may be used by unauthorized individuals to authenticate to RustFS services or hijack sessions.
- Insider Threat: Even users with limited access who can read logs may gain elevated access if they retrieve credential material.
- Compliance Risk: Logging sensitive authentication material may violate organizational policies and industry compliance standards (e.g., PCI-DSS, SOC2, ISO 27001) that forbid exposure of authentication secrets in logs

### Remediation
- Do not include secrets in log output — redact secret_key, session_token, and similar fields.
- Log only safe identifiers such as non-sensitive IDs (e.g., parent_user, trace ID).

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-r54g-49rx-98cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-24762
- https://github.com/rustfs/rustfs
