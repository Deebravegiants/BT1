# [C] agent-js: Insecure Key Generation in `Ed25519KeyIdentity.generate`

## Summary
Severity: Critical
Advisory: GHSA-c9vv-fhgv-cjc3
CVE: CVE-2024-1631
CWE: CWE-321, CWE-330
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-c9vv-fhgv-cjc3
Type: github-advisory

## Affected
- npm: `@dfinity/identity` — affected >=0.20.0-beta.0 <1.0.1
- npm: `@dfinity/auth-client` — affected >=0.20.0-beta.0 <1.0.1

## Details
## Impact

The library offers a function to generate an ed25519 key pair via `Ed25519KeyIdentity.generate` with an optional param to provide a 32 byte seed value, which will then be used as the secret key. **When no seed value is provided, it is expected that the library generates the secret key using secure randomness**. However, a recent change **broke this guarantee** and **uses an insecure seed for key pair generation**.

Since the private key of this identity (`535yc-uxytb-gfk7h-tny7p-vjkoe-i4krp-3qmcl-uqfgr-cpgej-yqtjq-rqe`) is compromised, one could lose funds associated with the principal on ledgers or lose access to a canister where this principal is the controller. Users are asked to take proactive measures mentioned below in Workarounds:Users to protect their assets. 

## Patches
Patch for the vulnerability is **available in v1.0.1** for all the packages listed in the advisory. Please upgrade and deploy your canisters immediately. 

## Workarounds

### Developers

The recommended fix is to upgrade the package to the patched version. If that is not possible, there are couple of workarounds to handle the insecure key generation.

1. Invoking the function as `Ed25519KeyIdentity.generate(null)` would fix the broken conditional evaluation and force the function to generate a securely random seed. However, this is not guaranteed to work for future upgrades.
2. Passing a securely generated randomness as a seed to `Ed25519KeyIdentity.generate` would force the library to use it as the seed to generate the key pair.

### Users

#### Removing a controller of a canister if it's the affected principal

For all canisters you control, fetch the controllers of the canisters using 
```sh
dfx canister info --ic <CANISTER>
```
If you see the principal `535yc-uxytb-gfk7h-tny7p-vjkoe-i4krp-3qmcl-uqfgr-cpgej-yqtjq-rqe` as one of the controllers, follow the steps below 
```sh
dfx identity whoami # record CURRENT_IDENTITY

dfx identity new <NEW_IDENTITY_NAME> 
dfx identity use <NEW_IDENTITY_NAME> 
dfx identity get-principal <NEW_IDENTITY_NAME> # record NEW_IDENTITY_PRINCIPAL

dfx identity use <CURRENT_IDENTITY>
dfx canister update-settings --ic <CANISTER> --add-controller <NEW_IDENTITY_PRINCIPAL>
dfx canister update-settings --ic <CANISTER> --remove-controller `535yc-uxytb-gfk7h-tny7p-vjkoe-i4krp-3qmcl-uqfgr-cpgej-yqtjq-rqe`
```
For more details on canister management, please visit [here](https://internetcomputer.org/docs/current/tutorials/developer-journey/level-1/1.6-managing-canisters)

#### Checking funds on wallets /  ledgers

If you have funds on ledgers using a browser wallet, please check if the account principal matches `535yc-uxytb-gfk7h-tny7p-vjkoe-i4krp-3qmcl-uqfgr-cpgej-yqtjq-rqe`. If it does, please create a new account and transfer the funds to the new account immediately.

## References

1. [fix PR link](https://github.com/dfinity/agent-js/pull/851)
2. [NPM patched version](https://www.npmjs.com/package/@dfinity/identity/v/1.0.1)
3. [agent-js Github repo](https://github.com/dfinity/agent-js)
4. [agent-js docs](https://agent-js.icp.xyz/identity/index.html)

## References
- https://github.com/dfinity/agent-js/security/advisories/GHSA-c9vv-fhgv-cjc3
- https://nvd.nist.gov/vuln/detail/CVE-2024-1631
- https://github.com/dfinity/agent-js/pull/851
- https://agent-js.icp.xyz/identity/index.html
- https://github.com/dfinity/agent-js
- https://www.npmjs.com/package/@dfinity/identity/v/1.0.1
