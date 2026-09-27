# [H] langflow: /profile_pictures/{folder_name}/{file_name} endpoint file reading

## Summary
Severity: High
Advisory: GHSA-ph9w-r52h-28p7
CVE: CVE-2026-33497
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-ph9w-r52h-28p7
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.7.1

## Details
## Vulnerability

### Path Traversal in `GET /api/v1/files/profile_pictures/{folder_name}/{file_name}`

The `download_profile_picture` function in `src/backend/base/langflow/api/v1/files.py` constructed file paths by directly concatenating the user-supplied `folder_name` and `file_name` path parameters without sanitization or boundary validation. The resulting path was passed to the filesystem without verifying it remained within the intended directory.

An unauthenticated attacker could supply traversal sequences (e.g. `../secret_key`) to navigate outside the profile pictures directory and read arbitrary files on the server filesystem.

This exposed the server to:

- **Sensitive file disclosure** — any file readable by the application process could be retrieved
- **Secret key exfiltration** — the application's `secret_key` file, used as JWT signing material, could be read directly via `../secret_key`
- **Authentication bypass** — with the `secret_key` in hand, an attacker can forge valid JWT tokens and authenticate as any user, including administrators

---

## Proof of Concept

```bash
curl --path-as-is 'http://<host>:7860/api/v1/files/profile_pictures/../secret_key'
```

A successful response returns the raw secret key value used to sign all JWT authentication tokens in the instance.

---

## Fix

The fix was applied in `src/backend/base/langflow/api/v1/files.py` (PR #12263).

Two layers of defense were introduced:

**1. Typed path validation** — the `folder_name` and `file_name` parameters were changed from plain `str` to `ValidatedFolderName` and `ValidatedFileName` annotated types that reject traversal characters at the FastAPI input layer.

**2. Path containment check** — `Path.name` is used to strip any directory component from the inputs before path construction, and `Path.is_relative_to()` verifies the resolved path remains within the allowed base directory. This replaces the previous `startswith()` check, which was susceptible to prefix-ambiguity bugs.

```diff
 @router.get("/profile_pictures/{folder_name}/{file_name}")
 async def download_profile_picture(
-    folder_name: str,
-    file_name: str,
+    folder_name: ValidatedFolderName,
+    file_name: ValidatedFileName,
     settings_service: Annotated[SettingsService, Depends(get_settings_service)],
 ):
```

```diff
-        file_path = (config_path / "profile_pictures" / folder_name / file_name).resolve()
+        safe_folder = Path(folder_name).name
+        safe_file = Path(file_name).name
+        file_path = (config_path / "profile_pictures" / safe_folder / safe_file).resolve()

         allowed_base = (config_path / "profile_pictures").resolve()
-        if not str(file_path).startswith(str(allowed_base)):
-            raise HTTPException(status_code=404, detail="Profile picture not found")
+        if not file_path.is_relative_to(allowed_base):
+            raise HTTPException(status_code=404, detail="Profile picture not found")
```

---

## Workarounds

If you cannot upgrade immediately, restrict network access to the `/api/v1/files/profile_pictures/` endpoint at the reverse-proxy or firewall level. Rotating the `secret_key` is strongly recommended if exposure cannot be ruled out.

---

## Acknowledgements

We thank the security researcher who responsibly disclosed this vulnerability.

- [r00tuser111](https://github.com/r00tuser111)

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-ph9w-r52h-28p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33497
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-81.yaml
