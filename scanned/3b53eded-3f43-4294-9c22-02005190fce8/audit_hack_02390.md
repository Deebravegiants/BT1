# [M] Medium

## Summary
Severity: Medium
Source: https://github.com/BeamNetwork/deployment-nicks-method/blob/8a8b2d3356db689ae09c6c9bc1affc86f83684f0/index.js#L40
Type: audit-issue

## Details
Components: all

Hard-coded booleans, numbers, and strings in the code are hard to understand, and they are prone to error, because after some time, their origin and context can be forgotten or mistaken.

For example:

In `deployment-nicks-method`:

* [index.js](https://github.com/BeamNetwork/deployment-nicks-method/blob/8a8b2d3356db689ae09c6c9bc1affc86f83684f0/index.js#L40)[:L40](https://github.com/BeamNetwork/deployment-nicks-method/blob/8a8b2d3356db689ae09c6c9bc1affc86f83684f0/index.js#L40)

In `beam-bootstrap-chain`:

* [BeamBootstrap.sol](https://github.com/BeamNetwork/beam-bootstrap-chain/blob/96beab1c5cfd41310bfba733ab7216426caf4a38/contracts/BeamBootstrap.sol#L17)[:L17](https://github.com/BeamNetwork/beam-bootstrap-chain/blob/96beab1c5cfd41310bfba733ab7216426caf4a38/contracts/BeamBootstrap.sol#L17): hard-coded `20`
* [truffle.js](https://github.com/BeamNetwork/beam-bootstrap-chain/blob/96beab1c5cfd41310bfba733ab7216426caf4a38/truffle.js#L9)[:L9](https://github.com/BeamNetwork/beam-bootstrap-chain/blob/96beab1c5cfd41310bfba733ab7216426caf4a38/truffle.js#L9): hard-coded address

In `policed-contracts`:

* [Policy.sol](https://github.com/BeamNetwork/policed-contracts/blob/f9299f43e2bf3629bee2f82bf637918ac9221d62/contracts/Policy.sol#L59)[:L59](https://github.com/BeamNetwork/policed-contracts/blob/f9299f43e2bf3629bee2f82bf637918ac9221d62/contracts/Policy.sol#L59): hard-coded address
* `erc820.js`:[L5](https://github.com/BeamNetwork/policed-contracts/blob/f9299f43e2bf3629bee2f82bf637918ac9221d62/erc820.js#L5): bytecode without comment
* `erc820.js`:[L9](https://github.com/BeamNetwork/policed-contracts/blob/f9299f43e2bf3629bee2f82bf637918ac9221d62/erc820.js#L9): hard-coded address
* `erc820.js`:[L10](https://github.com/BeamNetwork/policed-contracts/blob/f9299f43e2bf3629bee2f82bf637918ac9221d62/erc820.js#L10): hard-coded address

Consider defining a constant variable for every hard-coded value, giving it a clear and explanatory name. For the complex values, consider adding a comment explaining how they were calculated or why they were chosen.

**_Update:_** _Fixed. All the hard-coded values mentioned above have been moved to constants, commented, or removed._
