# [H] changedetection.io has an Arbitrary Local File Read via a crafted backup restore

## Summary
Severity: High
Advisory: GHSA-8757-69j2-hx56
CVE: CVE-2026-43891
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-8757-69j2-hx56
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.55.1

## Details
### Details
The vulnerability is caused by trusting attacker-controlled snapshot paths restored from backup files.

The vulnerable flow starts in the backup restore logic. When a backup ZIP is restored, the application extracts the archive and copies each restored watch UUID directory directly into the live datastore using `shutil.copytree(entry.path, dst_dir)`. This preserves attacker-controlled files inside the restored watch directory, including `history.txt`.

Relevant code:
- [changedetectionio/blueprint/backups/restore.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/blueprint/backups/restore.py#L132)
- [changedetectionio/blueprint/backups/restore.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/blueprint/backups/restore.py#L141)

After restore, the application parses `history.txt` in the watch `history` property. This is the core trust-boundary issue.

Relevant code:
- [changedetectionio/model/Watch.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/model/Watch.py#L460)
- [changedetectionio/model/Watch.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/model/Watch.py#L471)
- [changedetectionio/model/Watch.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/model/Watch.py#L478)

The relevant logic is effectively:

```python
if os.sep not in v and '/' not in v and '\\' not in v:
    v = os.path.join(self.data_dir, v)
else:
    snapshot_fname = os.path.basename(v)
    proposed_new_path = os.path.join(self.data_dir, snapshot_fname)
    if not os.path.exists(v) and os.path.exists(proposed_new_path):
        v = proposed_new_path
```

This has the following security consequence:

- If the `history.txt` value is only a filename, it is resolved safely under `self.data_dir`.
- If the value contains path separators, it is treated as a path reference rather than a watch-local snapshot name.
- If that external path already exists, it is preserved unchanged.

As a result, a malicious restored `history.txt` entry such as:

`1776969105,/etc/passwd`

will be accepted if the referenced file exists and is readable by the application process.

The second vulnerable step is in `get_history_snapshot()`. Once the untrusted path has been accepted into the watch history, the application reads the resolved path directly without enforcing that it remains inside the watch directory.

Relevant code:
- [changedetectionio/model/Watch.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/model/Watch.py#L554)

That function eventually performs direct file reads such as:

```python
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    return f.read()
```

The third step is reachability. The trusted history entry is consumed by both the Preview UI and the watch history API.

Relevant code:
- [changedetectionio/blueprint/ui/preview.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/blueprint/ui/preview.py#L77)
- [changedetectionio/api/Watch.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/api/Watch.py#L263)

In the Preview flow, the application selects the latest history timestamp and calls:

```python
content = watch.get_history_snapshot(timestamp=timestamp)
```

In the API flow, the application also calls:

```python
content = watch.get_history_snapshot(timestamp=timestamp)
```

This creates the following end-to-end exploit chain:

1. An attacker supplies a crafted backup ZIP.
2. The restore process preserves attacker-controlled `history.txt`.
3. The `history.txt` parser accepts an absolute or out-of-directory path if that path exists.
4. Preview or the history API dereferences the stored path directly.
5. The application returns the contents of the targeted local file.

The root cause is that imported history entries are treated as trusted filesystem paths instead of being restricted to safe basenames under `watch.data_dir`.


### PoC
The following proof of concept demonstrates the end-to-end exploit chain. It assumes the attacker has gained access to the backup restore functionality to upload the crafted archive.

1. Create a normal watch in the UI, for example:
```text
https://example.com
```

2. Trigger at least one successful check so the watch generates a valid history entry and can later be included in a backup.

<img width="1230" height="587" alt="image" src="https://github.com/user-attachments/assets/a76302c9-48d6-4aa3-9bfc-0ba2fdb31156" />

3. Go to the `Backups` section and create a backup archive.

<img width="1232" height="390" alt="image" src="https://github.com/user-attachments/assets/8fef0444-d8f0-4db6-be75-04fa7db2fec8" />

4. Extract the backup archive and identify the watch UUID directory that contains the target watch's `watch.json`. For example:
```text
5db3d3d8-71e6-4db2-a81e-e1f0445c3e47
```

5. Open that watch directory and edit `history.txt`.

6. Replace the latest history entry with a path to an existing local file that is readable by the application process. For example:
```text
1776969188,/etc/passwd
```

If the timestamp differs in the extracted backup, keep the original latest timestamp and only replace the filename/path portion.

Example:
```text
1776969188,742215043ff9be7e635f05e680ff9b11.txt
```

becomes:

```text
1776969188,/etc/passwd
```

<img width="1139" height="366" alt="image" src="https://github.com/user-attachments/assets/07277b36-4747-4181-82d1-523385b40de3" />

7. Repack the backup so that the UUID directories are located at the root of the ZIP archive.

Important:
- Do not add an extra parent directory layer when repacking.
- The archive root should contain directories such as:
```text
<watch-uuid>/
<group-uuid>/
changedetection.json
url-list.txt
```

<img width="986" height="353" alt="image" src="https://github.com/user-attachments/assets/21b30368-2cb5-4b88-9055-79d5bf06ad48" />

8. In the UI, restore the modified backup and enable replacement of existing watches with the same UUID.

<img width="1229" height="700" alt="image" src="https://github.com/user-attachments/assets/79abd9d2-8b2d-4e08-abf3-3b63238a8055" />

9. After restore completes, open `Preview` for the restored watch.

10. The application will read the attacker-controlled path from `history.txt` and display the contents of the referenced local file instead of the original watch snapshot.

Observed result:
- The Preview page returns the content of the attacker-selected local file.

Expected result:
- The application should reject absolute paths or out-of-directory paths restored from `history.txt`.
- Snapshot history should be restricted to files within the watch's own data directory.

Optional API verification:
- The same issue can also be confirmed through the watch history API by requesting the modified timestamp after restore.
- The API returns the same file content because it also calls `watch.get_history_snapshot(timestamp=timestamp)` on the trusted history entry.

<img width="1233" height="545" alt="image" src="https://github.com/user-attachments/assets/a2814a5a-2cdd-49a1-916b-c956dd5fda1f" />

### Impact
This is an arbitrary local file disclosure vulnerability reachable through malicious backup restore content.

Who is impacted:
- Deployments where the application process has read access to sensitive local system files.
- Docker or host-mounted environments where secrets, config files, or operational artifacts are explicitly readable by the service.

What can be exposed:
- **Arbitrary System Files:** Core operating system files (e.g., `/etc/passwd`, `/proc/self/environ`), system-level configurations, and host metrics.
- **Application Data:** Internal records and files residing under the /datastore directory.
- **Secrets & Artifacts:** Application-local configuration files, API tokens, database credentials, and other sensitive artifacts accessible to the application process.

By accessing the backup restore functionality and importing a crafted archive, an attacker can exploit the application's fail-open path validation. The confidentiality impact is exceptionally high because, once the payload is ingested, the application can be manipulated to disclose arbitrary local system files and highly sensitive environment variables directly through standard UI or API responses.

### Recommendation
The application should treat all paths restored from `history.txt` as untrusted input.

The root cause is in [changedetectionio/model/Watch.py](https://github.com/dgtlmoon/changedetection.io/blob/master/changedetectionio/model/Watch.py#L460), where values containing path separators are currently accepted as filesystem paths and preserved if the referenced file already exists.

The fix should be:

1. Never trust absolute or external paths from `history.txt`.
2. Normalize every history entry to `os.path.basename(v)`.
3. Join the normalized filename to `self.data_dir`.
4. Skip the entry if the resolved file does not exist inside the watch directory.

Suggested code change:

```python
snapshot_fname = os.path.basename(v.strip())
resolved_path = os.path.join(self.data_dir, snapshot_fname)

if not os.path.exists(resolved_path):
    logger.warning(
        f"Skipping unsafe or missing history entry for {self.get('uuid')}: {v!r}"
    )
    continue

tmp_history[k] = resolved_path
```

This ensures restored history entries can only reference files inside the watch's own data directory and prevents arbitrary local file reads through Preview or the history API.

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-8757-69j2-hx56
- https://github.com/pocket-id/pocket-id/security/advisories/GHSA-w6p7-2fxx-4f44
- https://nvd.nist.gov/vuln/detail/CVE-2026-43891
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/pypa/advisory-database/tree/main/vulns/changedetection-io/PYSEC-2026-30.yaml
