# [H] [i18next] Prototype pollution attack

## Summary
Severity: High
Program: Node.js third-party modules
Weakness: Modification of Assumed-Immutable Data (MAID)
Reporter: 0b5cur17y
State: resolved
Disclosed: 2021-04-26T20:52:07.700Z
Source: https://hackerone.com/reports/968355

## Details
I would like to report a prototype pollution vulnerability in i18next.
It allows to modify the prototype of a base object, which may result in DoS, XSS, RCE, etc. depending on the way the library is used.

# Module

**module name:** i18next
**version:** 19.7.0
**npm page:** ` https://www.npmjs.com/package/i18next`

## Module Description

i18next is a very popular internationalization framework for browser or any other javascript environment (eg. node.js).

## Module Stats

Weekly downloads: 1,003,465

# Vulnerability

## Vulnerability Description

The i18next API provides a function `addResourceBundle` in [src/ResourceStore.js:79](https://github.com/i18next/i18next/blob/master/src/ResourceStore.js#L79) (see API docs [here](https://www.i18next.com/overview/api#addresourcebundle)).
It allows to set many translations at once. Optionally, it can process nested objects and overwrite existing translations.
For example, you can call `i18next.addResourceBundle('en', 'translations', { homepage: { title: 'The English Title'} }, true, true);` to set the key "homepage.title" to "The English Title", overwriting it if it existed before.

The function `addResourceBundle` uses a utility function `deepExtend` to process nested objects.
It is defined in [src/utils.js:84](https://github.com/i18next/i18next/blob/44c2e7621a7e07660433b27122281b50886a1caf/src/utils.js#L84).
This function attempts to guard against prototype pollution by blacklisting the property `__proto__`.
However, it does not blacklist the property `constructor`.

To pollute `Object` you could thus set a translation like `{ constructor: { prototype: { polluted: true } } }`.

For an application to be vulnerable, it has to use  `addResourceBundle` with attacker-controlled input passed into the `resources` argument.
Moreover, both arguments `deep` and `overwrite` must be set to `true`. 

## Steps To Reproduce:

To try it out quickly, you can just copy the function `deepExtend` from [src/utils.js:84](https://github.com/i18next/i18next/blob/44c2e7621a7e07660433b27122281b50886a1caf/src/utils.js#L84)

_Trimmed to 38 lines — full report: https://hackerone.com/reports/968355_
