# [M] Important Security Rule Violation

## Summary
Severity: Medium
Reporter: 0xSmartContract
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/hardhat.config.js#L78
Type: audit-issue

## Details
# Important Security Rule Violation

## Summary
One of the most important checklists in the Smart Kontract writing process is the seed - private key - mnemonic specifications.

Direct "mnemonic" information is given in the hardhat.config.js file, this is an unacceptable design method even for testing and bypasses the most important security consideration. It may inadvertently expose such information later in the project.


## Vulnerability Detail

Mnemonic (or seed) phrases are combinations of 12 words set in a specific order, which allow you to restore access to a crypto wallet. Essentially, they are “the last line of defense” alongside private keys (the password that lets you spend coins). If someone gets ahold of one, they can get full access to your wallet and funds that are being kept in it.

In short, you shouldn’t upload your private keys or seed phrase on public, open-source repositories such as GitHub—or anywhere else that's public for that matter.

The most important security principle by the coding teams; Even if there is a test, such a use should not be made because it is a known fact that it is very natural to skip the test and truth distinction.

It doesn't matter if the vulnerability is exploitable or whether its content is tested, even the accuracy of this mnemonic has not been tested and it doesn't matter.

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/hardhat.config.js#L78

## Impact

https://decrypt.co/30222/hacker-steals-1200-worth-of-ethereum-in-under-100-seconds

## Code Snippet

hardhat.config.js#L78:
```js
  networks: {
    hardhat: {
      accounts: {
        mnemonic:
          'apart turn peace asthma useful mother tank math engine usage prefer orphan exile fold squirrel',
      },
    },
```


## Tool used

Manual Review

## Recommendation

The privatekey-seed management style of Consensys should be adopted, it is a very dangerous habit to write such information even if it is a test

https://consensys.net/blog/developers/how-to-avoid-uploading-your-private-key-to-github-approaches-to-prevent-making-your-secrets-public/
