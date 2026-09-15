# [C] Flair 0.15.0 and 0.15.1 Deserialization of Untrusted Data via ClusteringModel.load

## Summary
Severity: Critical
Advisory: CVE-2026-76843
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-76843
Type: osv

## Details
The official Flair wheels for 0.15.0 and 0.15.1 still contain flair/models/clustering.py, whose ClusteringModel.load static method returns pickle.loads(joblib.load(str(model_file))) and so executes arbitrary Python while loading a model file. Loading a model supplied by an attacker therefore runs that attacker's code with the privileges of the loading process. This is the same sink and the same file as CVE-2024-10073, which records 0.15.0 as the fixed version on the basis that clustering support was dropped in that release; the module was removed from the documented API but remains present in the distributed artifact and reachable by importing flair.models.clustering directly, so the earlier record's fixed version does not hold for the shipped package.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76843.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76843
- https://www.vulncheck.com/advisories/flair-and-deserialization-of-untrusted-data-via-clusteringmodel-load
- https://github.com/flairNLP/flair
- https://pypi.org/project/flair/
- https://pypi.org/project/flair/0.15.1/
- https://github.com/flairNLP/flair/blob/v0.14.0/flair/models/clustering.py
