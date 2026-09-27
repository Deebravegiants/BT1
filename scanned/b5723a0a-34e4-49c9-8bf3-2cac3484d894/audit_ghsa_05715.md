# [M] RustFS has IAM Incorrect Authorization in ImportIam that Allows Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-vcwh-pff9-64cc
CVE: CVE-2026-22042
CWE: CWE-285
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-vcwh-pff9-64cc
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=0 <1.0.0-alpha.79

## Details
### Summary

The `ImportIam` admin API validates permissions using **`ExportIAMAction`** instead of **`ImportIAMAction`**, allowing a principal with *export-only* IAM permissions to perform *import* operations. Since importing IAM data performs privileged **write** actions (creating/updating users, groups, policies, and service accounts), this can lead to **unauthorized IAM modification and privilege escalation**.

---

### Details

In `ImportIam`, the authorization check is implemented as follows:

```rust
validate_admin_request(
    &req.headers,
    &cred,
    owner,
    false,
    vec![Action::AdminAction(AdminAction::ExportIAMAction)],
).await?;
```

However, this code resides in the **Import IAM** operation (`struct ImportIam {}`), which performs **state-changing IAM writes**.

The expected behavior is to validate against **`AdminAction::ImportIAMAction`** (or an equivalent import-specific admin action), not `ExportIAMAction`.

---

### PoC

**Prerequisites**

1. A RustFS deployment with IAM enabled.
2. An IAM user or role that has **Export IAM** permission but **does not** have Import IAM or full admin permissions.
3. Access credentials for that user.

**Steps**

1. Create or obtain an IAM principal with permission equivalent to:

   ```
   AdminAction::ExportIAMAction
   ```

   and without Import IAM privileges.

2. Prepare a valid IAM import ZIP archive containing, for example:

   * A new policy granting administrative permissions
   * A user or service account bound to that policy

3. Send a request to the Import IAM endpoint (the same endpoint handled by `ImportIam::call`), authenticating with the export-only credentials.

4. Observe that:

   * The request passes authorization.
   * IAM entities from the archive are created or modified successfully.

**Expected Result**

* The request should be rejected with an authorization error (e.g., AccessDenied).

**Actual Result**

* The request succeeds, and IAM state is modified.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-vcwh-pff9-64cc
- https://nvd.nist.gov/vuln/detail/CVE-2026-22042
- https://github.com/rustfs/rustfs
