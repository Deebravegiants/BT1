# [H] High

## Summary
Severity: High
Source: https://github.com/BeamNetwork/currency/tree/af3428020545e3f3ae2f3567b94e1fbc5e5bdb4c#eco-currency-and-governance-currency
Type: audit-issue

## Details
Components: all

There are no test coverage reports on any of the repositories. Without these reports, it is impossible to know whether there are parts of the code which are never executed by the automated tests. For every change, a full manual test suite has to be executed to make sure that nothing is broken or misbehaving.

Consider adding the test coverage reports and making it reach at least 95% of the source code.

**_Update:_** _Partially fixed. The_ [_test coverage report_](https://github.com/BeamNetwork/currency/tree/af3428020545e3f3ae2f3567b94e1fbc5e5bdb4c#eco-currency-and-governance-currency) _was added to the currency repository, reporting 92% of coverage. Eco’s statement for this issue:_

> Test coverage of our contracts is around 98%. Our overall coverage reporting includes the additional JavaScript tooling included in the repository, used for deployment and testing. Coverage on the JavaScript code is intentionally less thorough, approximately 87%. This allows us to iterate more quickly on the JavaScript code, while still covering the core functionality.
