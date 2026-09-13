# [M] Gogs has a Denial of Service in repository/wiki file listing web pages

## Summary
Severity: Medium
Advisory: GHSA-3qq3-668m-v9mj
CVE: CVE-2025-64719
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-3qq3-668m-v9mj
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
### Summary
A malicious user with rights to create a new file on a repository or wiki page can trigger a denial of service condition in which the pages containing the listing of files will return HTTP error 500 and render the web interface unusable for the repository or wiki.

### Details
The issue is present in file `internal/route/repo/wiki.go` and `internal/route/repo/view.go` where the pages try to recover commit information. If errors are returned while recovering commit information, the page will return a 500 error and stop rendering, resulting in a denial of service.
In `view.go` the issue occurs at [line 56](https://github.com/gogs/gogs/blob/89f0f86c7e1a3be7f48d99e27818a79d17357558/internal/route/repo/view.go#L56) while a slightly different issue occurs in `wiki.go` at [line 174](https://github.com/gogs/gogs/blob/89f0f86c7e1a3be7f48d99e27818a79d17357558/internal/route/repo/wiki.go#L174) where `commits[0]` is dereferenced without checking if it contains value.
It is possible to trigger issues in assigning the correct value to variable `commits` by using a specific string as part of the page title. 
The issue is linked to the fact that file names can contain special characters such as `*`, `?`, `[`, `]`, etc. that will be interpreted as git's pathspec instead of a simple string. So crafting a name containing an incomplete pathspec sequence will trigger this error.

### PoC
As a proof of concept consider the file name `"[]` and how it affects repository and wiki pages.
In the following images it is shown how pages are created, the error shown in the web page right after creation and the error as logged in the console.

<img width="835" height="503" alt="repo_creation" src="https://github.com/user-attachments/assets/cdee9625-33d9-42d3-a5fa-264fba4923ed" />

**Figure 1: Creation of malicious file in repository**

<img width="832" height="692" alt="repo_error_web" src="https://github.com/user-attachments/assets/53c57366-8f45-4a0f-a2ac-86f4a08467cc" />

**Figure 2: Malicious file in repository causes error 500**

<img width="934" height="56" alt="repo_error_console" src="https://github.com/user-attachments/assets/26427fc3-bead-4e41-a484-e2d53289a2da" />

**Figure 3: Console error caused by malicious file in repository**

<img width="835" height="503" alt="wiki_creation" src="https://github.com/user-attachments/assets/7a5c9836-64e3-4824-b6e5-9f9a80e7f18a" />

**Figure 4: Creation of malicious file in wiki**

<img width="1001" height="463" alt="wiki_error_web" src="https://github.com/user-attachments/assets/33c5a907-b81c-4157-bd37-33341412172a" />

**Figure 5: Malicious file in wiki causes error 500**

<img width="1018" height="537" alt="wiki_error_console" src="https://github.com/user-attachments/assets/9b0ab551-5720-4715-a2ac-f7310534f025" />

**Figure 6: Console error caused by malicious file in wiki**

### Impact
The repository and wiki pages will not render when files named with the payload are present in the repository or in the wiki.
This condition will be present as long as the malicious file is present in the repository or wiki. The issue will not cause a DoS condition when using the server via CLI.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-3qq3-668m-v9mj
- https://nvd.nist.gov/vuln/detail/CVE-2025-64719
- https://github.com/gogs/gogs/pull/8116
- https://github.com/gogs/gogs/commit/ae41bab5f28e4880edcef01c91d2cbb8839ec9e4
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
