# [M] Storing Password in Local Storage

## Summary
Severity: Medium
Advisory: GHSA-wvh7-5p38-2qfc
CWE: CWE-256
Ecosystem: npm
Published: 2020-07-23
Source: https://github.com/advisories/GHSA-wvh7-5p38-2qfc
Type: github-advisory

## Affected
- npm: `parse` — affected >=0 <2.10.0

## Details
The `setPassword` method (http://parseplatform.org/Parse-SDK-JS/api/2.9.1/Parse.User.html#setPassword) stores the user's password in localStorage as raw text making it vulnerable to anyone with access to your localStorage. We believe this is the only time that password is stored at all. In the documentation under Users > Signing Up, it clearly states, "We never store passwords in plaintext, nor will we ever transmit passwords back to the client in plaintext."

Example Code:
```js
async () => {
    const user = Parse.User.current()
    if (user) {
        user.setPassword('newpass')
        await user.save()
    }
}
```
After running the above code, the new password will be stored in localStorage as a property named "password".

Proposed Solution:
Before saving anything to localStorage, Parse should strip out any properties named "password" that are attempting to be stored with a Parse.User type object.

Configuration:
Parse SDK: 2.9.1
Parse Server: 3.9.0

## References
- https://github.com/parse-community/Parse-SDK-JS/security/advisories/GHSA-wvh7-5p38-2qfc
- https://github.com/parse-community/Parse-SDK-JS/commit/d1106174571b699f972929dd7cbb8e45b5283cbb
- https://github.com/parse-community/Parse-SDK-JS
