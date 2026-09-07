# [M] LangChain has incomplete f-string validation in prompt templates

## Summary
Severity: Medium
Advisory: GHSA-926x-3r5x-gfhw
CVE: CVE-2026-40087
CWE: CWE-1336, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-926x-3r5x-gfhw
Type: github-advisory

## Affected
- PyPI: `langchain-core` — affected >=0 <0.3.84
- PyPI: `langchain-core` — affected >=1.0.0a1 <1.2.28

## Details
LangChain's f-string prompt-template validation was incomplete in two respects.

First, some prompt template classes accepted f-string templates and formatted them without enforcing the same attribute-access validation as `PromptTemplate`. In particular, `DictPromptTemplate` and `ImagePromptTemplate` could accept templates containing attribute access or indexing expressions and subsequently evaluate those expressions during formatting.

Examples of the affected shape include:

```python
"{message.additional_kwargs[secret]}"
"https://example.com/{image.__class__.__name__}.png"
```

Second, f-string validation based on parsed top-level field names did not reject nested replacement fields inside format specifiers. For example:

```python
"{name:{name.__class__.__name__}}"
```

In this pattern, the nested replacement field appears in the format specifier rather than in the top-level field name. As a result, earlier validation based on parsed field names did not reject the template even though Python formatting would still attempt to resolve the nested expression at runtime.

## Affected usage

This issue is only relevant for applications that accept untrusted template strings, rather than only untrusted template variable values.

In addition, practical impact depends on what objects are passed into template formatting:

- If applications only format simple values such as strings and numbers, impact is limited and may only result in formatting errors.
- If applications format richer Python objects, attribute access and indexing may interact with internal object state during formatting.

In many deployments, these conditions are not commonly present together. Applications that allow end users to author arbitrary templates often expose only a narrow set of simple template variables, while applications that work with richer internal Python objects often keep template structure under developer control. As a result, the highest-impact scenario is plausible but is not representative of all LangChain applications.

Applications that use hardcoded templates or that only allow users to provide variable values are not affected by this issue.

## Impact

The direct issue in `DictPromptTemplate` and `ImagePromptTemplate` allowed attribute access and indexing expressions to survive template construction and then be evaluated during formatting. When richer Python objects were passed into formatting, this could expose internal fields or nested data to prompt output, model context, or logs.

The nested format-spec issue is narrower in scope. It bypassed the intended validation rules for f-string templates, but in simple cases it results in an invalid format specifier error rather than direct disclosure. Accordingly, its practical impact is lower than that of direct top-level attribute traversal.

Overall, the practical severity depends on deployment. Meaningful confidentiality impact requires attacker control over the template structure itself, and higher impact further depends on the surrounding application passing richer internal Python objects into formatting.

## Fix

The fix consists of two changes.

First, LangChain now applies f-string safety validation consistently to `DictPromptTemplate` and `ImagePromptTemplate`, so templates containing attribute access or indexing expressions are rejected during construction and deserialization.

Second, LangChain now rejects nested replacement fields inside f-string format specifiers.

Concretely, LangChain validates parsed f-string fields and raises an error for:

- variable names containing attribute access or indexing syntax such as `.` or `[]`
- format specifiers containing `{` or `}`

This blocks templates such as:

```python
"{message.additional_kwargs[secret]}"
"https://example.com/{image.__class__.__name__}.png"
"{name:{name.__class__.__name__}}"
```

The fix preserves ordinary f-string formatting features such as standard format specifiers and conversions, including examples like:

```python
"{value:.2f}"
"{value:>10}"
"{value!r}"
```

In addition, the explicit template-validation path now applies the same structural f-string checks before performing placeholder validation, ensuring that the security checks and validation checks remain aligned.

## References
- https://github.com/langchain-ai/langchain/security/advisories/GHSA-926x-3r5x-gfhw
- https://nvd.nist.gov/vuln/detail/CVE-2026-40087
- https://github.com/langchain-ai/langchain/pull/36612
- https://github.com/langchain-ai/langchain/pull/36613
- https://github.com/langchain-ai/langchain/commit/6bab0ba3c12328008ddca3e0d54ff5a6151cd27b
- https://github.com/langchain-ai/langchain/commit/af2ed47c6f008cdd551f3c0d87db3774c8dfe258
- https://github.com/langchain-ai/langchain
- https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D0.3.84
- https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D1.2.28
