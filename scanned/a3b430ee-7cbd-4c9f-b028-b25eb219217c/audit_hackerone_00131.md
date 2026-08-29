# [M] ReDoS in syntax highlighting due to Rouge

## Summary
Severity: Medium
Program: GitLab
Weakness: Uncontrolled Resource Consumption
Reporter: doyensec
State: resolved
Disclosed: 2021-11-15T14:53:39.705Z
Source: https://hackerone.com/reports/1283484

## Details
### Summary

Gitlab is using the ruby gem "rouge" which has a ReDoS vulnerability. In rouge, the lexers used to parse programming languages rely heavily on regular expressions. Some of the regular expressions have cubic worst-case complexity and are vulnerable to Regular Expression Denial of Service (ReDoS). By crafting malicious input, an attacker can cause Denial of Service.

In Gitlab, rouge is used for syntax highlighting when viewing source code files and when rendering markdown (issues, comments, wiki pages, etc.).

We first reported the vulnerability to rouge on 9 March 2021. As it remains unfixed and Gitlab is vulnerable, we are reporting here for your information.

### Rouge bug in detail

The vulnerable lexer regular expressions are below. Line numbers refer to the latest rouge version (3.26.0).

**Factor**
lib/rouge/lexers/factor.rb line 246
Pattern: `"""\s+.*?\s+"""`
As the two `\s+` groups and the `.*` group match spaces, a long string of spaces with no final `"""` will cause catastrophic backtracking.

**GHC Core**
lib/rouge/lexers/ghc_core.rb line 20
Pattern: `^Result size of .+\s*.*}`
Again, .+ \s* and .* all match spaces, so by not ending in a }, the regex will backtrack.

**Ceylon**
lib/rouge/lexers/ceylon.rb line 54
Pattern: `.*``.*``.*"`
The three .* groups match backticks as well, so if a long string of backticks doesn't end in a ", backtracking will occur. To cause ReDoS, an initial double quote is required.

The Factor and Ceylon regexes have been fixed on master (https://github.com/rouge-ruby/rouge/commit/78af25c2dd69be8ce0a83eb368ddcafe7cc294c4) but a new version has not been released. GHC Core has not been fixed.

__Recipes for creating source code files which cause ReDoS:__

GHC Core (.dump-cse): `'Result size of ' + ' ' * 3456`
Factor (.factor): `'"""' + ' ' * 3456`
Ceylon (.ceylon): ``'"' + '`' * 3456``

As the worst-case complexity is cubic, doubling the length of the repeating part (spaces or backticks) makes processing take 8 times as long.

### Steps to reproduce

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1283484_
