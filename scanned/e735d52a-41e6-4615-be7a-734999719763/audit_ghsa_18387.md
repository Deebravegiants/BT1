# [H] buildalon/setup-steamcmd leaked authentication token in job output logs

## Summary
Severity: High
Advisory: GHSA-mj96-mh85-r574
CWE: CWE-532
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-mj96-mh85-r574
Type: github-advisory

## Affected
- GitHub Actions: `buildalon/setup-steamcmd` — affected >=0 <1.1.0

## Details
### Summary
Log output includes authentication token that provides full account access

### Details
The post job action prints the contents of `config/config.vdf` which holds the saved authentication token and can be used to sign in on another machine. This means any public use of this action leaves authentication tokes for the associated steam accounts publicly available. Additionally, `userdata/$user_id$/config/localconfig.vdf` contains potentially sensitive information which should not be included in public logs.

### PoC
Use the following workflow step
```
steps:
      - name: Setup SteamCMD
        uses: buildalon/setup-steamcmd@v1.0.4

      - name: Sign into steam
        shell: bash
        run: |
          steamcmd +login ${{ secrets.WORKSHOP_USERNAME }} ${{ secrets.WORKSHOP_PASSWORD }} +quit
```

### Impact
Anyone who has used this workflow action with a steam account is affected and has had valid authentication tokens leaked in the job logs. This is particularly bad for public repositories, as anyone with a GitHub account can access the logs and view the token.

## References
- https://github.com/buildalon/setup-steamcmd/security/advisories/GHSA-mj96-mh85-r574
- https://github.com/buildalon/setup-steamcmd/commit/c3301963a182b14fd7a5b4991e6ae91ed39e4a5c
- https://github.com/buildalon/setup-steamcmd
