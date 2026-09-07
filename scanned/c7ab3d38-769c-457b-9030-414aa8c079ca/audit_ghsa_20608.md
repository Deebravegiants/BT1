# [C] React Editable Json Tree vulnerable to arbitrary code execution via function parsing

## Summary
Severity: Critical
Advisory: GHSA-j3rv-w43q-f9x2
CVE: CVE-2022-36010
CWE: CWE-95
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-j3rv-w43q-f9x2
Type: github-advisory

## Affected
- npm: `react-editable-json-tree` — affected >=0 <2.2.2

## Details
### Impact
Our library allows strings to be parsed as functions and stored as a specialized component, [`JsonFunctionValue`](https://github.com/oxyno-zeta/react-editable-json-tree/blob/09a0ca97835b0834ad054563e2fddc6f22bc5d8c/src/components/JsonFunctionValue.js). To do this, Javascript's [`eval`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval) function was used to execute strings that begin with "function" as Javascript. This was an oversight that unfortunately allows arbitrary code to be executed if it exists as a value within the JSON structure being displayed. Given that this component may often be used to display data from arbitrary, untrusted sources, this is extremely dangerous.

One important note is that users who have defined a custom [`onSubmitValueParser`](https://github.com/oxyno-zeta/react-editable-json-tree/tree/09a0ca97835b0834ad054563e2fddc6f22bc5d8c#onsubmitvalueparser) callback prop on the [`JsonTree`](https://github.com/oxyno-zeta/react-editable-json-tree/blob/09a0ca97835b0834ad054563e2fddc6f22bc5d8c/src/JsonTree.js) component should be ***unaffected***. This vulnerability exists in the default `onSubmitValueParser` prop which calls [`parse`](https://github.com/oxyno-zeta/react-editable-json-tree/blob/master/src/utils/parse.js#L30).

### Patches
We have decided on a two-pronged approach to patching this vulnerability:

1. Create a patch update that adds a workaround **which is not enabled by default** to preserve backwards-compatibility
2. On the next major update, **we will enable this workaround by default**

The workaround we have decided on is adding a prop to `JsonTree` called `allowFunctionEvaluation`. This prop will be set to `true` in v2.2.2, so you can upgrade without fear of losing backwards-compatibility.

We have also implemented additional security measures as we know many people may not read the details of this vulnerability, and we want to do the best we can to keep you protected. In v2.2.2, we switched from using `eval` to using [`Function`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function) to construct anonymous functions. This is better than `eval` for the following reasons:

- Arbitrary code should not be able to execute immediately, since the `Function` constructor explicitly *only creates* anonymous functions
- Functions are created without local closures, so they only have access to the global scope

This change has brought a *slight* potential for breaking backwards-compatibility if users for some reason were relying on side-effects of our usage of `eval`, but that is beyond intended behavior, so we have decided to go ahead with this change and consider it a non-breaking change.

### Workarounds
As mentioned above, there are a few scenarios you must consider:

If you use:
- **Version `<2.2.2`**, you must upgrade as soon as possible.
- **Version `^2.2.2`**, you must explicitly set `JsonTree`'s `allowFunctionEvaluation` prop to `false` to fully mitigate this vulnerability.
- **Version `>=3.0.0`**, `allowFunctionEvaluation` is already set to `false` by default, so no further steps are necessary.

### References
None.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [GitHub repo](https://github.com/oxyno-zeta/react-editable-json-tree)

## References
- https://github.com/oxyno-zeta/react-editable-json-tree/security/advisories/GHSA-j3rv-w43q-f9x2
- https://nvd.nist.gov/vuln/detail/CVE-2022-36010
- https://github.com/oxyno-zeta/react-editable-json-tree
- https://github.com/oxyno-zeta/react-editable-json-tree/releases/tag/2.2.2
