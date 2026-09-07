# [H] NLTK: Model-artifact APIs bypass pathsec and touch files outside allowed roots

## Summary
Severity: High
Advisory: GHSA-8mgp-746c-j5xp
CVE: CVE-2026-81726
CWE: CWE-22, CWE-59, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-8mgp-746c-j5xp
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0

## Details
### Summary

Several model-artifact APIs still treat caller-controlled model paths as ordinary filenames even when NLTK path security is enforced. The same outside-root paths are rejected by guarded helpers, but these public read and write flows still use raw file APIs.

### Details

- **Vulnerability type:** File sandbox bypass
- **Affected component:** `TransitionParser.train`, `TransitionParser.parse`, `AveragedPerceptron.save`, `AveragedPerceptron.load`, `PerceptronTagger.save_to_json`, `save_maxent_params`
- **Affected versions:** Published `3.9.4` and current source `v3.10.0-rc2` both reproduced.
- **Patched versions:** Not yet patched
- **Root cause:** Model import and export helpers use built-in `open()` on caller-controlled paths instead of pathsec-aware helpers.

`TransitionParser.train()` writes outside allowed roots, `TransitionParser.parse()` reads outside allowed roots, `AveragedPerceptron` bypasses the sandbox in both directions, and adjacent read-side helpers in the same family already show the intended guarded behavior. I confirmed outside-root reads and writes while `pathsec.open()` or the guarded sibling helpers rejected the same paths.

### PoC

**Preconditions**
- The application enables `pathsec` enforcement and lets untrusted workflows choose model import or export paths.

**Steps**
1. Enable `pathsec.ENFORCE=True` and restrict allowed roots to a dedicated sandbox directory.
2. Use public model import or export APIs with paths that point outside that root.
3. Observe the same paths are rejected by negative-control guarded helpers such as `pathsec.open()`, `PerceptronTagger.load_from_json()`, or `load_maxent_params()`.
4. Observe the vulnerable APIs still read or write outside-root files successfully.

**Minimal reproducible excerpt**

```text
transition_train_exists True
transition_parse_loader_read_bytes 13
averaged_load_keys ['bias']
maxent_save wrote ['alwayson.tab', 'labels.txt']
```

### Impact

Consumers that rely on `pathsec` for local containment can be tricked into reading or overwriting files outside approved roots through normal model persistence and loading APIs.

### Remediation

Route all model-path file access through `nltk.pathsec.open()` or existing pathsec-aware helpers, and add regression tests that pair each vulnerable API with a negative control on the same path.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-8mgp-746c-j5xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-81726
- https://github.com/nltk/nltk/pull/3757
- https://github.com/nltk/nltk/pull/3759
- https://github.com/nltk/nltk/pull/3813
- https://github.com/nltk/nltk/commit/2a92b71827d754ae8920261e7ed0c4bb283ab2d7
- https://github.com/nltk/nltk/commit/a44a7af69bca87e92d9c4a701fcbbe4512e8d450
- https://github.com/nltk/nltk/commit/cbc98458b43de5f792f0382583c16df39e5c5117
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-3740.yaml
- https://www.vulncheck.com/advisories/nltk-through-3.10.3-path-traversal-via-model-artifact-apis
