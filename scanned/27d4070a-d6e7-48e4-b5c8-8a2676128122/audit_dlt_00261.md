# [M] CL-2022-01: Github Account hijacking

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Multiple
Published: 2023-05-03
Source: https://notes.ethereum.org/OYu_JZWpQI2r9kPfgw2hMA
Type: ef-disclosure

## Details
# Account takeover

Short description
*
1 sentence description of the bug
RCE when installing repo due to broken repository hijacking
Attack scenario
*
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
When I analyzed your github repo for bug bounty, I found that you recently changed the github user from eth2-clients to eth-clients without thinking the impact that will cause. The old username was available so I take it for PoC. I am able now to fork real repo and place secretly malicious code inside. So, every old urls will be redirected to my repo. I'm a white hat so I will not create same repo to not impact users.
Impact
*
 Describe the effect this may have in a production setting
As an attacker, I can fork real repositories and host malicious content on the compromised Github repositories. I can also host an SDK or malware or a simple backdoor which can lead to an RCE. With malicious code, a hacker can steal hot wallet private key!
Components
*
Point to the files, functions, and/or specific line numbers where the bug occurs
Total 25 places are affected from ethereum, chainsafe & prysmaticlabs github repo (and website docs) are affected. Chainsafe is critical (bc it's on .gitmodules), others are low just a compromised url.
Reproduction
*
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
No tools are used to find the bug. Go to https://github.com/eth2-clients and you will see the takeover message.

As an example of RCE PoC for Chainsafe, do this 3 commands:
(I'm a white hat, I will never impact users, there is no malicious code)

1. $ git clone --recurse-submodules --remote-submodules https://github.com/ChainSafe/slashing-protection-interchange-tests.git

2. $ cd slashing-protection-interchange-tests/slashing-protection-interchange-tests

3. $ cat README.md

You will see the Takeover message
Fix
Description of suggested fix, if available
Change the repo url.

And for future be careful when changing github username. Popular repositories (more than 100 forks) are not vulnerable by this when changing username.

_Trimmed to 38 lines — full report: https://notes.ethereum.org/OYu_JZWpQI2r9kPfgw2hMA_
