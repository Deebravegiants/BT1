# [H] Prototype Pollution in JSON5 via Parse Method

## Summary
Severity: High
Advisory: GHSA-9c47-m6qq-7p4h
CVE: CVE-2022-46175
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2022-12-29
Source: https://github.com/advisories/GHSA-9c47-m6qq-7p4h
Type: github-advisory

## Affected
- npm: `json5` — affected >=2.0.0 <2.2.2
- npm: `json5` — affected >=0 <1.0.2

## Details
The `parse` method of the JSON5 library before and including version `2.2.1` does not restrict parsing of keys named `__proto__`, allowing specially crafted strings to pollute the prototype of the resulting object.

This vulnerability pollutes the prototype of the object returned by `JSON5.parse` and not the global Object prototype, which is the commonly understood definition of Prototype Pollution. However, polluting the prototype of a single object can have significant security impact for an application if the object is later used in trusted operations.

## Impact
This vulnerability could allow an attacker to set arbitrary and unexpected keys on the object returned from `JSON5.parse`. The actual impact will depend on how applications utilize the returned object and how they filter unwanted keys, but could include denial of service, cross-site scripting, elevation of privilege, and in extreme cases, remote code execution.

## Mitigation
This vulnerability is patched in json5 v2.2.2 and later. A patch has also been backported for json5 v1 in versions v1.0.2 and later.

## Details
 
Suppose a developer wants to allow users and admins to perform some risky operation, but they want to restrict what non-admins can do. To accomplish this, they accept a JSON blob from the user, parse it using `JSON5.parse`, confirm that the provided data does not set some sensitive keys, and then performs the risky operation using the validated data:
 
```js
const JSON5 = require('json5');

const doSomethingDangerous = (props) => {
  if (props.isAdmin) {
    console.log('Doing dangerous thing as admin.');
  } else {
    console.log('Doing dangerous thing as user.');
  }
};

const secCheckKeysSet = (obj, searchKeys) => {
  let searchKeyFound = false;
  Object.keys(obj).forEach((key) => {
    if (searchKeys.indexOf(key) > -1) {
      searchKeyFound = true;
    }
  });
  return searchKeyFound;
};

const props = JSON5.parse('{"foo": "bar"}');
if (!secCheckKeysSet(props, ['isAdmin', 'isMod'])) {
  doSomethingDangerous(props); // "Doing dangerous thing as user."
} else {
  throw new Error('Forbidden...');
}
```
 
If the user attempts to set the `isAdmin` key, their request will be rejected:
 
```js
const props = JSON5.parse('{"foo": "bar", "isAdmin": true}');
if (!secCheckKeysSet(props, ['isAdmin', 'isMod'])) {
  doSomethingDangerous(props);
} else {
  throw new Error('Forbidden...'); // Error: Forbidden...
}
```
 
However, users can instead set the `__proto__` key to `{"isAdmin": true}`. `JSON5` will parse this key and will set the `isAdmin` key on the prototype of the returned object, allowing the user to bypass the security check and run their request as an admin:
 
```js
const props = JSON5.parse('{"foo": "bar", "__proto__": {"isAdmin": true}}');
if (!secCheckKeysSet(props, ['isAdmin', 'isMod'])) {
  doSomethingDangerous(props); // "Doing dangerous thing as admin."
} else {
  throw new Error('Forbidden...');
}
 ```

## References
- https://github.com/json5/json5/security/advisories/GHSA-9c47-m6qq-7p4h
- https://nvd.nist.gov/vuln/detail/CVE-2022-46175
- https://github.com/json5/json5/issues/199
- https://github.com/json5/json5/issues/295
- https://github.com/json5/json5/pull/298
- https://github.com/json5/json5/commit/62a65408408d40aeea14c7869ed327acead12972
- https://github.com/json5/json5/commit/7774c1097993bc3ce9f0ac4b722a32bf7d6871c8
- https://github.com/json5/json5
- https://lists.debian.org/debian-lts-announce/2023/11/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3S26TLPLVFAJTUN3VIXFDEBEXDYO22CE
