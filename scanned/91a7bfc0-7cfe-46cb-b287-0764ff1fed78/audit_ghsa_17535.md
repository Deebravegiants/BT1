# [M] PowSyBl Core contains Polynomial REDoS’es

## Summary
Severity: Medium
Advisory: GHSA-rqpx-f6rc-7hm5
CVE: CVE-2025-48058
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-19
Source: https://github.com/advisories/GHSA-rqpx-f6rc-7hm5
Type: github-advisory

## Affected
- Maven: `com.powsybl:powsybl-commons` — affected >=0 <6.7.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

This is an advisory for a **potential polynomial Regular Expression Denial of Service (ReDoS)** vulnerability in the PowSyBl's DataSource mechanism. When the `listNames(String regex)` method is called on a DataSource, the user-supplied regular expression (which may be unvalidated) is compiled and evaluated against a collection of file-like resource names.

To trigger a **polynomial ReDoS** via this mechanism, **two attacker-controlled conditions** must be met:
- **Control over the regex input** passed into `listNames(String regex)`.
  - _Example:_ An attacker supplies a malicious pattern like `(.*a){10000}`.
- **Control or influence over the file/resource names** being matched.
  - _Example:_ Filenames such as `"aaaa...!"` that induce regex engine backtracking.

If both conditions are satisfied, a malicious actor can cause **significant CPU consumption** due to regex backtracking — even
with polynomial patterns. Since both inputs can be controlled via a publicly accessible method or external filesystem handling,
the `listNames(String regex)` method is considered vulnerable to polynomial **REDoS**.

Unlike classic _catastrophic exponential_ ReDoS, this subtle attack exploits a greedy `.*` prefix followed by a fixed suffix, repeated multiple times.  
When applied to long filenames that almost match the pattern, the regex engine performs extensive backtracking, degrading performance predictably with input size. In a multi-tenant environment, an attacker can degrade the performance - and thereby the availability - of the server to an extent that it affects other users of the application. This can for example be useful if an attacker wants to delay other users in a scenario where a time advantage can be a competitive advantage.  
A tricky part in this is that the attacker needs to control both the pattern and the input which may not always be the case.

#### Am I impacted?
You are vulnerable if you make direct calls to the `listNames(String regex)` method on a class implementing the `ReadOnlyDataSource` interface, don't control the regular expression used as `regex` parameter, and if this datasource points to an archive or directory where an untrusted user may edit the filenames.
For instance, this could be the case if you want to list the files made available by a datasource which names respect a user-provided regular expression.
Note that only direct calls to this method are concerned. There are several usages of this method in powsybl, but the provided regular expressions are all hardcoded and therefore cannot be provided by a malicious user.

### Patches
com.powsybl:powsybl-commons:6.7.2 and higher

### References
[powsybl-core v6.7.2](https://github.com/powsybl/powsybl-core/releases/tag/v6.7.2)

## References
- https://github.com/powsybl/powsybl-core/security/advisories/GHSA-rqpx-f6rc-7hm5
- https://nvd.nist.gov/vuln/detail/CVE-2025-48058
- https://github.com/powsybl/powsybl-core/commit/72f79dec6d4292f892fbddd68a19c67935c7d81f
- https://github.com/powsybl/powsybl-core
- https://github.com/powsybl/powsybl-core/releases/tag/v6.7.2
