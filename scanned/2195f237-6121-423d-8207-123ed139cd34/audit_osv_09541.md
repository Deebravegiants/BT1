# [H] CVE-2017-1000106

## Summary
Severity: High
Advisory: CVE-2017-1000106
Aliases: GHSA-qgjq-m78x-4gm8
CVSS: 8.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-1000106
Type: osv

## Details
Blue Ocean allows the creation of GitHub organization folders that are set up to scan a GitHub organization for repositories and branches containing a Jenkinsfile, and create corresponding pipelines in Jenkins. Its SCM content REST API supports the pipeline creation and editing feature in Blue Ocean. The SCM content REST API did not check the current user's authentication or credentials. If the GitHub organization folder was created via Blue Ocean, it retained a reference to its creator's GitHub credentials. This allowed users with read access to the GitHub organization folder to create arbitrary commits in the repositories inside the GitHub organization corresponding to the GitHub organization folder with the GitHub credentials of the creator of the organization folder. Additionally, users with read access to the GitHub organization folder could read arbitrary file contents from the repositories inside the GitHub organization corresponding to the GitHub organization folder if the branch contained a Jenkinsfile (which could be created using the other part of this vulnerability), and they could provide the organization folder name, repository name, branch name, and file name.

## References
- https://jenkins.io/security/advisory/2017-08-07/
