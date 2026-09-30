# [H] Use of Out-of-range Pointer Offset in the Elasticsearch Machine Learning Native Inference Process

## Summary
Severity: High
Advisory: BIT-elasticsearch-2026-72642
Aliases: CVE-2026-72642
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-72642
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.5.0 <9.5.1

## Details
The native inference process that Elasticsearch uses to evaluate uploaded machine learning models accepts a model operation that computes a memory address from an offset supplied inside the model, without validating that the offset stays within the bounds of the underlying storage. A user with the privileges required to upload and deploy a trained model can craft a model that reads and writes memory outside the intended allocation. The result is heap corruption that crashes the inference process, and, with sufficient control over the heap layout, could allow arbitrary code execution in the context of that process.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-4-5-9-5-1-security-update-esa-2026-123/389504
- https://nvd.nist.gov/vuln/detail/CVE-2026-72642
