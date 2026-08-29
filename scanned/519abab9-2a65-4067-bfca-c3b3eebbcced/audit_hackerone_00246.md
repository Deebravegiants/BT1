# [H] "Secure View" aka "Hide Download" can be bypassed easily

## Summary
Severity: High
Program: Nextcloud
Weakness: Improper Access Control - Generic
Reporter: at5djl3pwjmunyutnoatp
State: resolved
Disclosed: 2020-04-10T09:12:36.773Z
CVE: CVE-2020-8139
Source: https://hackerone.com/reports/788257

## Details
The mid-2019 announced feature "Secure view" (https://nextcloud.com/blog/secure-view-prevent-your-shared-files-from-getting-downloaded/) allows for hiding the Download button on public shares.
Even though the announcement admits that there are always workarounds out there to get hands on the file anyway, the workaround for this one is way too simple: Just add **/download** to the URL (like you used to for every public share) and your browser starts downloading unhesitently.

For the sharee, the checkbox "Hide Download" is therefore very deceptive, since they very likely weigh themselves in false safety.

## Impact

Download a copy of a file or folder that's not supposed to be downloaded whatsoever
