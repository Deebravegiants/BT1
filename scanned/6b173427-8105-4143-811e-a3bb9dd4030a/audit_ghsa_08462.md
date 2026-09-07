# [H] Kata Container has CopyFile Policy Subversion via Symlinks

## Summary
Severity: High
Advisory: GHSA-q49m-57vm-c8cc
CVE: CVE-2026-41326
CWE: CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-q49m-57vm-c8cc
Type: github-advisory

## Affected
- Go: `github.com/kata-containers/kata-containers` — affected >=0 <0.0.0-20260422180503-1b9e49eb2763

## Details
### Summary
An oversight in the CopyFile policy (and perhaps the CopyFile handler) allows untrusted hosts to write to arbitrary locations inside the guest workload image. This can be used to overwrite binaries inside the guest and exfiltrate data from containers; even those running inside CVMs.

### Details
Here is the policy that covers CopyFile requests.
```
CopyFileRequest if {
    print("CopyFileRequest: input.path =", input.path)
        
    check_directory_traversal(input.path)
        
    some regex1 in policy_data.request_defaults.CopyFileRequest
    regex2 := replace(regex1, "$(sfprefix)", policy_data.common.sfprefix)
    regex3 := replace(regex2, "$(cpath)", policy_data.common.cpath)
    regex4 := replace(regex3, "$(bundle-id)", "[a-z0-9]{64}")
    print("CopyFileRequest: regex4 =", regex4)
    
    regex.match(regex4, input.path)
      
    print("CopyFileRequest: true")
}
```
This checks that files are being copied to `policy_data.common.cpath`, which is typically set to `/run/kata-containers/shared/containers`. In other words, you're allowed to copy files to anywhere inside the shared dir.

For reference, here is the CopyFile message. Note that none of the other fields are check in the policy.
```
message CopyFileRequest {
	// Path is the destination file in the guest. It must be absolute,
	// canonical and below /run.
	string path = 1;
	// FileSize is the expected file size, for security reasons write operations
	// are made in a temporary file, once it has the expected size, it's moved
	// to the destination path.
	int64 file_size = 2;
	// FileMode is the file mode.
	uint32 file_mode = 3;
	// DirMode is the mode for the parent directories of destination path.
	uint32 dir_mode = 4;
	// Uid is the numeric user id.
	int32 uid = 5;
	// Gid is the numeric group id.
	int32 gid = 6;
	// Offset for the next write operation.
	int64 offset = 7;
	// Data to write in the destination file.
	bytes data = 8;
}
```

In addition to copying files directly, the Kata Agent supports creating symlinks via the CopyFile API. In this case the `path` is the symlink name and the `data` field contains the symlink target. Given that the policy only checks the path, an attacker can craft a CopyFile request that results in a symlink going from any location into the shared dir.

### PoC
The above primitive can be used to to write arbitrary data into container images (pulled in the guest or otherwise). A couple steps are required.

First, identify some target path in the guest image. This could be a binary that will be called by the workload. You could also experiment with overwriting other stuff.

Create a symlink from this binary to the shared dir. The path/link name should be in the shared dir and the data/target should point to the path of the target file inside the container image in the guest fs.

Create a second CopyFile request to copy your data from the host into the symlink you just created in the shared dir. This will then be propagated into the image. You may want to restart the container to ensure that your new binary is invoked.

### Impact
Anyone who is using the upstream `genpolicy` implementation and expects it to prevent host access to container images is vulnerable This includes Confidential Containers workloads where the trust model explicitly forbids this type of access. If you have your own policy implementation you may or may not be vulnerable. If you do not care about protecting the image from the host (e.g. you are using unprotected host pull), you are not vulnerable.

This was individually discovered and reported by

- @calonso-nv 
- @fikriwahab
- @kodareef5

## References
- https://github.com/kata-containers/kata-containers/security/advisories/GHSA-q49m-57vm-c8cc
- https://nvd.nist.gov/vuln/detail/CVE-2026-41326
- https://github.com/kata-containers/kata-containers/commit/1b9e49eb2763aa6ea6a99b276d3ff5e2c7f658f2
- https://github.com/kata-containers/kata-containers
- http://www.openwall.com/lists/oss-security/2026/05/13/2
