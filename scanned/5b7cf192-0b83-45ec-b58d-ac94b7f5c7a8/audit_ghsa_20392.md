# [H] Inefficient Regular Expression Complexity in nltk (word_tokenize, sent_tokenize)

## Summary
Severity: High
Advisory: GHSA-f8m6-h2c7-8h9x
CVE: CVE-2021-43854
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-f8m6-h2c7-8h9x
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.6.6

## Details
### Impact
The vulnerability is present in [`PunktSentenceTokenizer`](https://www.nltk.org/api/nltk.tokenize.punkt.html#nltk.tokenize.punkt.PunktSentenceTokenizer), [`sent_tokenize`](https://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.sent_tokenize)  and [`word_tokenize`](https://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.word_tokenize). Any users of this class, or these two functions, are vulnerable to a Regular Expression Denial of Service (ReDoS) attack. 
In short, a specifically crafted long input to any of these vulnerable functions will cause them to take a significant amount of execution time. The effect of this vulnerability is noticeable with the following example:
```python
from nltk.tokenize import word_tokenize

n = 8
for length in [10**i for i in range(2, n)]:
    # Prepare a malicious input
    text = "a" * length
    start_t = time.time()
    # Call `word_tokenize` and naively measure the execution time
    word_tokenize(text)
    print(f"A length of {length:<{n}} takes {time.time() - start_t:.4f}s")
```
Which gave the following output during testing:
```python
A length of 100      takes 0.0060s
A length of 1000     takes 0.0060s
A length of 10000    takes 0.6320s
A length of 100000   takes 56.3322s
...
```
I canceled the execution of the program after running it for several hours.

If your program relies on any of the vulnerable functions for tokenizing unpredictable user input, then we would strongly recommend upgrading to a version of NLTK without the vulnerability, or applying the workaround described below.

### Patches
The problem has been patched in NLTK 3.6.6. After the fix, running the above program gives the following result:
```python
A length of 100      takes 0.0070s
A length of 1000     takes 0.0010s
A length of 10000    takes 0.0060s
A length of 100000   takes 0.0400s
A length of 1000000  takes 0.3520s
A length of 10000000 takes 3.4641s
```
This output shows a linear relationship in execution time versus input length, which is desirable for regular expressions.
We recommend updating to NLTK 3.6.6+ if possible.

### Workarounds
The execution time of the vulnerable functions is exponential to the length of a malicious input. With other words, the execution time can be bounded by limiting the maximum length of an input to any of the vulnerable functions. Our recommendation is to implement such a limit.

### References
* The issue showcasing the vulnerability: https://github.com/nltk/nltk/issues/2866
* The pull request containing considerably more information on the vulnerability, and the fix: https://github.com/nltk/nltk/pull/2869
* The commit containing the fix: 1405aad979c6b8080dbbc8e0858f89b2e3690341
* Information on CWE-1333: Inefficient Regular Expression Complexity: https://cwe.mitre.org/data/definitions/1333.html

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/nltk/nltk](https://github.com/nltk/nltk)
* Email us at [nltk.team@gmail.com](mailto:nltk.team@gmail.com)

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-f8m6-h2c7-8h9x
- https://nvd.nist.gov/vuln/detail/CVE-2021-43854
- https://github.com/nltk/nltk/issues/2866
- https://github.com/nltk/nltk/pull/2869
- https://github.com/nltk/nltk/commit/1405aad979c6b8080dbbc8e0858f89b2e3690341
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2021-859.yaml
