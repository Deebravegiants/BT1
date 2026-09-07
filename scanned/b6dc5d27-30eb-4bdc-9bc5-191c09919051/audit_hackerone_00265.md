# [M] Uncontrolled Resource Consumption in any Markdown field using Mermaid

## Summary
Severity: Medium
Program: GitLab
Weakness: Uncontrolled Resource Consumption
Reporter: ryhmnlfj
State: resolved
Disclosed: 2019-12-20T07:15:12.672Z
CVE: CVE-2019-15584, CVE-2019-9220
Source: https://hackerone.com/reports/670572

## Details
### Summary

I found a bypass for the mitigation of [DoS via Mermaid (CVE-2019-9220)](https://hackerone.com/reports/470067).
As the mitigation for [CVE-2019-9220](https://hackerone.com/reports/470067), the input limit of 5000 characters is currently applied to a Mermaid code block, but it can be bypassed by simply splitting the longer payload to **many** code blocks.

### Steps to reproduce

1. Sign in to GitLab.
2. Open any page where you can input Markdown text using Mermaid into the form.
3. Copy and paste the contents of the attached file (**"payload-5Kchars-x-100blocks.txt"**) to the input form.
4. Save the Markdown text on the page you opened. (For example, click "Comment" on "Issue" page. Please see "Example_on_Issue_page_Firefox.png")
5. Wait a few seconds for **many** Mermaid graphs to begin rendering.

{F551168}

### What is the current *bug* behavior?

When rendering of the Mermaid graphs starts, the browser tab displaying the page freezes.
This behavior prevents browsing and editing the page that have been added the Mermaid graphs.
Also, the resources used by the browser tab will increase as rendering continues. In the worst case, the entire browser also freezes or crashes.

### What is the expected *correct* behavior?

We need a mechanism to stop rendering in advance by detecting if the user's input contains a large number of Mermaid code blocks.

### Relevant logs and/or screenshots

* "payload-5Kchars-x-100blocks.txt" : This text contains 100 sets of Mermaid code blocks. Each code block contains approximately 5000 characters.
* "Example_on_Issue_page_Firefox.png" : Screenshot when pasting the payload on "Issue" page.

### Output of checks

This bug happens on the official Docker installation of GitLab Enterprise Edition `12.1.4-ee`.
The browsers used for testing are `Firefox 68` and `Chromium 76` on Ubuntu.

#### Results of GitLab environment info

Output of `sudo gitlab-rake gitlab:env:info`:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/670572_
