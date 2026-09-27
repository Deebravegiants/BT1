# [H] Immunefi: Sky Remote Code Execution Bugfix Review

## Summary
Severity: High
Published: Tue, 25 Feb 2025
Source: https://medium.com/immunefi/sky-remote-code-execution-bugfix-review-9bfbeb8c1c17?source=rss----6cdc579be8a0---4
Type: security-research

## Details
## ⚠️ THIS ARTICLE HAS MOVED

 This Medium version is archived and is no longer being updated. 

 Read the current and maintained version on the Immunefi Blog. 

 On 25 September 2023, a security researcher named xss submitted a critical vulnerability to Sky (formerly known as MakerDAO) through Immunefi. The white-hat was able to execute malicious code on vote.makerdao.com to extract sensitive content from the filesystem such as /etc/passwd. The vulnerability has since been fixed, on Sep 28, 2023.

 The report was validated and confirmed by the Sky team within two days, resulting in a maximum critical bounty payout of $50,000, as per their Bug Bounty Program (BBP) on Immunefi.

 Immunefi is pleased to have facilitated this responsible disclosure via our platform. Our goal is to make Web3 safer by incentivizing ethical hackers to responsibly disclose vulnerabilities in exchange for legitimate rewards and an enhanced reputation.

 Before diving into the root cause of the vulnerability, let’s first understand what Remote Code Execution (RCE) is and how it can impact DeFi applications and centralized exchanges.

## What is Remote code execution?

 RCE allows an attacker to remotely execute arbitrary commands or code on a server. For example, in an application that lets users ping a specified URL to check if an application is live, the code might resemble this:

 https://medium.com/media/1b2de693df4622bd448d26f44552319c/href Since the user-supplied value is directly added to the ping command without any sanitization to ensure it contains only the URL, an attacker can inject a command like this:

 https://medium.com/media/e59a5129ecd0087f9b8c445dd86afa8b/href The server will interpret whoami as a separate command due to the semicolon (;) and execute it after pinging the host, thus allowing the attacker to inject and execute any system command.

 Now, the question is: What can an attacker achieve through RCE on CeX or DeFi applications?

 - If the attacker has permission to modify file content, they could replace the wallet connection code on the DeFi application with a malicious script, which would initiate a transaction to the attacker’s wallet.

- The attacker might also be able to extract private keys or sensitive API keys/secrets, such as credentials for the email server.

- Even if the website doesn’t include Web3 business logic, the attacker could escalate their privileges to gain further access to the internal network.

## Root Cause of RCE on vote.makerdao.com

 vote.makerdao.com allows MKR token holders to vote and create proposals. When creating a proposal, users can either fill out the required fields manually or provide a URL to a .md file. If a user provides a Markdown file link, the application will parse the file content using gray-matter and auto-fill the proposal form.

 https://medium.com/media/549b4bcbcfecc8d2efc55462ad461b37/href Sky was using the gray-matter library without disabling the JavaScript engine feature, which runs eval on the provided Markdown. The eval function is a JavaScript feature that converts strings or expressions into executable code.

 https://medium.com/media/36c06203d68c60bdd9505578b9be921e/href Since the user could control the unsanitized Markdown input, the whitehat was able to inject the — javascript argument to make gray-matter execute system commands from the input.

 Here’s how the exploit works 

 - The attacker creates a poll at https://vote.makerdao.com/polling/create using the following URL: https://gist.githubusercontent.com/behroz-immunefi/1c664efb6bfaff4020fc6769fecd159b/raw/04649ac663f5095fa920bddb3d348d2622bc83d1/rce.md .

- After the poll is created, one can visit the following url endpoint https://vote.makerdao.com/api/polling/all-polls?network=goerli to view the output of the malicious command i.e cat /etc/passwd .

## Vulnerability Fix

 The vulnerability was fixed on Sep 28, 2023.

 Instead of passing Markdown content directly to the gray-matter library, it’s now routed through the matterWrapper function, which validates the input and disables the JavaScript engine by overriding the parse and stringify methods to return empty values.

 https://medium.com/media/0313cc2cadea1aa3a30cbe17bc44463e/href https://medium.com/media/15c77cde9d817ce8605bb8acb6f467fa/href Sky Remote Code Execution Bugfix Review was originally published in Immunefi on Medium, where people are continuing the conversation by highlighting and responding to this story.
