# [M] Data Leakage Vulnerability in livewire/livewire

## Summary
Severity: Medium
Advisory: GHSA-qwvp-268g-jjm8
CWE: CWE-200
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-qwvp-268g-jjm8
Type: github-advisory

## Affected
- Packagist: `livewire/livewire` — affected >=2.2.5 <2.2.6

## Details
livewire/livewire versions greater than 2.2.4 and less than 2.2.6 are affected by a data leakage vulnerability. The `$this->validate()` method, which is expected to return only the validated dataset, was returning all properties of the Livewire component. This regression introduced a security risk, allowing unvalidated data to be exposed, which could lead to unexpected behavior and potential security issues.

## References
- https://github.com/livewire/livewire/commit/6929f5882138a98187c196ce66cc689712c000af
- https://github.com/FriendsOfPHP/security-advisories/blob/master/livewire/livewire/2020-09-22-1.yaml
- https://github.com/livewire/livewire
- https://github.com/livewire/livewire/releases/tag/v2.2.6
