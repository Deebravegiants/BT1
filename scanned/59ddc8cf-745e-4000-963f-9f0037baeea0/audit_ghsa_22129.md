# [H] scikit-learn Denial of Service

## Summary
Severity: High
Advisory: GHSA-jxfp-4rvq-9h9m
CVE: CVE-2020-28975
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jxfp-4rvq-9h9m
Type: github-advisory

## Affected
- PyPI: `scikit-learn` — affected >=0.23.2 <1.0.1

## Details
svm_predict_values in svm.cpp in Libsvm v324, as used in scikit-learn 0.23.2 and other products, allows attackers to cause a denial of service (segmentation fault) via a crafted model SVM (introduced via pickle, json, or any other model permanence standard) with a large value in the _n_support array.
NOTE: the scikit-learn vendor's position is that the behavior can only occur if the library's API is violated by an application that changes a private attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28975
- https://github.com/scikit-learn/scikit-learn/issues/18891
- https://github.com/scikit-learn/scikit-learn/commit/1bf13d567d3cd74854aa8343fd25b61dd768bb85
- https://github.com/cjlin1/libsvm/blob/9a3a9708926dec87d382c43b203f2ca19c2d56a0/svm.cpp#L2501
- https://github.com/pypa/advisory-database/tree/main/vulns/scikit-learn/PYSEC-2020-108.yaml
- https://github.com/scikit-learn/scikit-learn
- https://security.gentoo.org/glsa/202301-03
- http://packetstormsecurity.com/files/160281/SciKit-Learn-0.23.2-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2020/Nov/44
